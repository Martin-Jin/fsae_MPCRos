#!/usr/bin/env python3
"""Bench steering calibration for the Arduino go-kart ECU - STEERING ONLY.

Talks straight to the ECU's serial port (no ROS) and sends `S<value> T0.0 B0.0` at 50 Hz.
Each Enter steps to the next S value, ramping at --ramp S units/s (the firmware has no rate
limit of its own), so you can measure the road-wheel angle at every step:

    S = 0, +30, +60, +90, +120, +180, 0, -30, -60, -90, -120, -180, 0

Each side is swept on its own because the firmware's S -> servo pulse map is not symmetric.
Throttle and brake are HARD-CODED to 0 - they are not options. With T0 the ECU never arms the
throttle (the go handshake also needs the brake held), but steering follows S even while the
ECU is disarmed, so the wheels WILL move: wheels off the ground, hands clear.

The ECU's #S telemetry (`#S<deg> T B E M F U`, M 0/1/2 = disarmed/armed/failsafe) is printed
twice a second, plus every non-telemetry line (READY, FAILSAFE, ...) in full.

When the script exits, frames stop and the ECU's 200 ms watchdog trips its failsafe: the
steering servo goes limp. That is expected. Reset the Arduino to clear it.

Refuses to start if anything else (serial_bridge!) has the port open. See
docs/NMPC_GOKART_GROUND_TEST.md (this branch) or docs/STANLEY_STEER_TEST.md
(test/planning-teleop-ground-test) for the table to fill in and where the results go.

Usage: scripts/steer_calibrate.py [--port /dev/serial/by-id/...] [--ramp 90]
"""
import argparse
import os
import sys
import threading
import time

import serial
import yaml

STEPS = [0, 30, 60, 90, 120, 180, 0, -30, -60, -90, -120, -180, 0]
SEND_HZ = 50.0
PARAMS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '..', 'common', 'fsae_bringup', 'config', 'fsae_params.yaml')


def default_port():
    try:
        with open(PARAMS) as f:
            return yaml.safe_load(f)['serial_bridge']['ros__parameters']['port']
    except (OSError, KeyError, TypeError, yaml.YAMLError) as e:
        sys.exit(f'could not read serial_bridge.port from {PARAMS} ({e}); pass --port')


def port_users(port):
    """PIDs (other than ours) holding the device open, from /proc/*/fd."""
    target = os.path.realpath(port)
    users = []
    for pid in filter(str.isdigit, os.listdir('/proc')):
        if int(pid) == os.getpid():
            continue
        fd_dir = f'/proc/{pid}/fd'
        try:
            for fd in os.listdir(fd_dir):
                if os.path.realpath(os.path.join(fd_dir, fd)) == target:
                    users.append(pid)
                    break
        except OSError:   # process gone, or not ours to inspect
            continue
    return users


class Sender:
    """Streams frames at 50 Hz on its own thread, ramping toward `target`."""

    def __init__(self, ser, ramp):
        self.ser = ser
        self.ramp = ramp
        self.target = 0.0
        self.current = 0.0
        self.running = True
        self.lock = threading.Lock()
        self.last_tel = ''
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        period = 1.0 / SEND_HZ
        step = self.ramp * period
        rx = b''
        next_tel_print = 0.0
        next_t = time.monotonic()
        while self.running:
            with self.lock:
                self.current += max(-step, min(step, self.target - self.current))
                s = self.current
            # T and B are fixed at 0.0 on purpose. Do not parameterise them.
            self.ser.write(f'S{s:.1f} T0.0 B0.0\n'.encode('ascii'))

            rx += self.ser.read(self.ser.in_waiting or 0)
            while b'\n' in rx:
                line, rx = rx.split(b'\n', 1)
                text = line.decode('ascii', errors='replace').strip()
                if text.startswith('#S'):
                    self.last_tel = text
                    if time.monotonic() >= next_tel_print:
                        print(f'    ECU {text}')
                        next_tel_print = time.monotonic() + 0.5
                elif text:
                    print(f'    ECU says: {text}')

            next_t += period
            time.sleep(max(0.0, next_t - time.monotonic()))

    def go_to(self, value):
        with self.lock:
            self.target = float(value)

    def at_target(self):
        with self.lock:
            return abs(self.current - self.target) < 1e-6


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--port', default=None, help='ECU serial port (default: serial_bridge.port '
                                                 'from fsae_params.yaml)')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--ramp', type=float, default=90.0, help='S units per second (default 90)')
    a = ap.parse_args()

    port = a.port or default_port()
    if not os.path.exists(port):
        sys.exit(f'{port} does not exist - is the Arduino plugged in?')
    users = port_users(port)
    if users:
        sys.exit(f'{port} is busy (open by PID {", ".join(users)}) - stop serial_bridge / the '
                 f'stack first (scripts/car.sh stop). Refusing to start.')
    try:
        # exclusive=True: nothing else can open the port while this runs.
        ser = serial.Serial(port, a.baud, timeout=0, exclusive=True)
    except (serial.SerialException, OSError) as e:
        sys.exit(f'could not open {port}: {e}')

    print(f'opened {port} @ {a.baud}. Sending S0.0 T0.0 B0.0 at {SEND_HZ:.0f} Hz '
          f'(throttle/brake fixed at 0), ramp {a.ramp:.0f} S/s.')
    print('WHEELS OFF THE GROUND, hands clear: steering moves even while the ECU is disarmed.')
    sender = Sender(ser, a.ramp)
    sender.thread.start()
    time.sleep(2.5)   # opening the port may reset the Arduino; let it boot on S0 frames

    try:
        for i, value in enumerate(STEPS):
            nxt = STEPS[i + 1] if i + 1 < len(STEPS) else None
            sender.go_to(value)
            while not sender.at_target():
                time.sleep(0.05)
            time.sleep(0.5)
            print(f'\n>>> S = {value:+d}  (last telemetry: {sender.last_tel or "none yet"})')
            print('    measure the road-wheel angle (left and right wheel), then', end=' ')
            if nxt is None:
                input('press Enter to finish (frames stop -> ECU failsafe, servo goes limp).')
            else:
                input(f'press Enter for S = {nxt:+d}  (Ctrl-C aborts)')
    except (KeyboardInterrupt, EOFError):
        print('\naborted - returning to S0 before stopping')
        sender.go_to(0.0)
        deadline = time.monotonic() + 3.0
        while not sender.at_target() and time.monotonic() < deadline:
            time.sleep(0.05)
    finally:
        sender.running = False
        sender.thread.join(timeout=1.0)
        ser.close()
        print('stopped sending. The ECU watchdog trips its failsafe within 200 ms (steering limp); '
              'reset the Arduino to clear it.')


if __name__ == '__main__':
    main()
