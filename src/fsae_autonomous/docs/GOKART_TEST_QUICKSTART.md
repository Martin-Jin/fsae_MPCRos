# Go-kart Stanley test: quickstart

Stanley steers the kart through the Arduino ECU, with a constant throttle. RViz runs on your
laptop over the zenoh bridge. Full details: [STANLEY_STEER_TEST.md](STANLEY_STEER_TEST.md),
[REMOTE_VIZ.md](REMOTE_VIZ.md).

> ⚠ **With `use_pad:=false` and `throttle:=` above 0, the kart drives itself about 10 s after start.** There
> is no pad and no deadman. Stop it with the **car e-stop**: it cuts the motor, the kart coasts
> (no brake) and steering stays live. Have someone on the e-stop before every start.

## 1. One-time laptop setup

Ubuntu 24.04 + ROS 2 Jazzy.

```bash
sudo apt install ros-jazzy-desktop python3-colcon-common-extensions
```

zenoh bridge, **exactly v1.10.1** (it must match the Jetson):

```bash
cd /tmp && curl -LO https://github.com/eclipse-zenoh/zenoh-plugin-ros2dds/releases/download/1.10.1/zenoh-plugin-ros2dds-1.10.1-x86_64-unknown-linux-gnu-standalone.zip
unzip -o zenoh-plugin-ros2dds-1.10.1-x86_64-unknown-linux-gnu-standalone.zip -d zenoh-bridge
install -Dm755 zenoh-bridge/zenoh-bridge-ros2dds ~/.local/bin/zenoh-bridge-ros2dds
zenoh-bridge-ros2dds --version    # "not found": log out and back in
```

Repo on the test branch, plus a small workspace (only the RViz/launch packages):

```bash
git clone git@github.com:UOA-FSAE/fsae_autonomous.git ~/repo/fsae_autonomous
cd ~/repo/fsae_autonomous && git checkout feat/first-lap && git pull
mkdir -p ~/fsae_ws/src && ln -s ~/repo/fsae_autonomous ~/fsae_ws/src/
source /opt/ros/jazzy/setup.bash
cd ~/fsae_ws && colcon build --base-paths src/fsae_autonomous/common/fsae_bringup src/fsae_autonomous/common/fsae_description
```

Already have it? Update instead:

```bash
cd ~/repo/fsae_autonomous && git checkout feat/first-lap && git pull
cd ~/fsae_ws && source /opt/ros/jazzy/setup.bash && colcon build --base-paths src/fsae_autonomous/common/fsae_bringup src/fsae_autonomous/common/fsae_description
```

## 2. Hotspot and the Jetson's IP

The Jetson joins the phone hotspot **`FSAE-Kart`** (password: ask the team). Any phone works if
it uses that exact name and password with WPA2-Personal security: the Jetson matches on those,
not on the phone. The IP does change with the phone, so look it up every session.

**Connect the laptop before the Jetson.** With the Jetson already on the hotspot, laptops have
repeatedly failed to join it (Windows logs "Dynamic key exchange did not succeed") and then
fall back to another saved network. The cause is not confirmed yet. Connecting in this order
avoids it:

1. Phone: hotspot on, band **2.4 GHz** (iPhone: **Maximise Compatibility** on), security
   **WPA2-Personal**, battery saver off. iPhone: keep the Personal Hotspot screen open until
   everything has joined, or it stops advertising.
2. Laptop: connect to `FSAE-Kart`. Check it stayed there (Wi-Fi icon), not on a campus network.
3. Power on the Jetson and wait about 1 min.
4. Find the Jetson's IP (last time: `10.170.134.157`):
   - **On the phone:** the hotspot's connected-devices list, entry `fsae-desktop`.
   - **Windows PowerShell:** `ping fsae-desktop.local` (mDNS usually does not reach WSL).
   - **From WSL:** `ip -br addr` shows the laptop's hotspot address; scan that subnet, for
     example:
     ```bash
     sudo apt install nmap && nmap -sn 172.20.10.0/28    # iPhone; Android uses a random /24
     ```
   - **Over the USB-C cable** (no Wi-Fi needed, see step 4): `ssh fsae@192.168.55.1 hostname -I`
     (use the hotspot one; `192.168.1.100` is the LiDAR port).

**Laptop won't join or keeps dropping:**
- **"Dynamic key exchange did not succeed"** (Event Viewer, WLAN-AutoConfig): forget
  `FSAE-Kart` (`netsh wlan delete profile name="FSAE-Kart"` in PowerShell) and rejoin, typing
  the password fresh. If the Jetson is already on, turn the hotspot off, connect the laptop
  first, then let the Jetson rejoin.
- **Windows keeps switching to another network:** untick "Connect automatically" on that
  network.
- **Hotspot not in the list at all:** the phone stopped advertising (iPhone screen closed,
  Android auto-off timer, battery saver). Toggle the hotspot off and on.
- **No internet on the hotspot:** ssh to the Jetson still works. Internet is only needed for
  `git pull` and installs.

**New phone or hotspot name:** rejoin the Jetson over USB-C with
`scripts/jetson-wifi.sh` (see [JETSON_TELEOP.md](JETSON_TELEOP.md)).

## 3. ssh key (once per laptop)

The Jetson password for `fsae`: ask Tommy.

```bash
ssh-keygen -t ed25519
ssh-copy-id fsae@<jetson-ip>
```

On first connect, accept only if the fingerprint is
`SHA256:jAMRGwBH5ZC/abJ08TArCv5h/8UxjIULdqfYVWlLOrs`.

Check: `ssh fsae@<jetson-ip> hostname` should print `fsae-desktop` without asking for a
password.

## 4. Every terminal

```bash
source /opt/ros/jazzy/setup.bash && source ~/fsae_ws/install/setup.bash && export FSAE_JETSON=fsae@<jetson-ip> && cd ~/repo/fsae_autonomous
ssh -o ConnectTimeout=5 $FSAE_JETSON hostname
```

- Expect `fsae-desktop`. A timeout means the laptop is not on `FSAE-Kart`, or the IP changed:
  fix it in the `export`. Without `ConnectTimeout`, ssh hangs for about 2 min before failing.
- Always set `FSAE_JETSON`. The script's built-in default IP is out of date.

**Wired instead** (USB-C cable laptop to Jetson, Jetson always `192.168.55.1`):

```bash
scripts/jetson-connect.sh
```

- Brings up the USB link in WSL (usbipd; may ask for `sudo` and, the first time, Windows UAC),
  then opens an ssh shell.
- For `car.sh` and the commands below, use `export FSAE_JETSON=fsae@192.168.55.1`.
- Give the cable back to Windows: `scripts/jetson-connect.sh --detach`.

## 5. Before starting

Hardware: ZED (USB), VLP-16 LiDAR (Ethernet + power), Arduino ECU (USB), servo power on.
Cones: blue on the left, yellow on the right.

```bash
ssh $FSAE_JETSON 'git -C ~/ros2_ws/src/fsae_autonomous branch --show-current; ls /dev/serial/by-id/; ip -br addr show enP8p1s0'
ssh $FSAE_JETSON 'curl -s http://192.168.1.201/cgi/status.json'
```

- Branch `feat/first-lap`, the same as the laptop.
- You need `usb-FTDI_FT232R_USB_UART_A5069RR4-if00-port0` (the Arduino).
- `enP8p1s0` must be **UP**. If it's DOWN, the LiDAR isn't connected: there will be no path,
  so no steering and no throttle.
- LiDAR status: `"motor":{"state":"On"`, rpm about 600, `"laser":{"state":"On"}`.

Clear anything left over from the last run (a recorder or a stack still running):

```bash
ssh $FSAE_JETSON 'tmux send-keys -t bag C-c 2>/dev/null; sleep 3; tmux kill-session -t bag 2>/dev/null; true'
scripts/car.sh stop
```

## 6. Start / RViz / stop (all from your laptop)

**Start.** The stack runs in tmux on the Jetson, so it survives Wi-Fi or ssh drops:

```bash
scripts/car.sh start fsae.launch.py drive:=true use_pad:=false throttle:=13
```

- Steering only, no throttle: leave out `throttle:=13`.
- `car.sh` adds `viz:=remote` (the car-side bridge for RViz) by itself. Pass `viz:=off` for a
  headless run.
- Recording a rosbag: [KART_RUN_COMMANDS.md](KART_RUN_COMMANDS.md).
- Steering scale/sign and Stanley gains are in `common/fsae_bringup/config/kart.yaml`.
- About 10 s after start the kart arms itself; the logs show `READY`, then `GO`.

**Check it's up** (wait about 15 s after start):

```bash
scripts/car.sh status
```

```bash
scripts/car.sh logs 60 | grep -E "READY|GO|FAILSAFE|#S"
```

`#S... M1 F0` = armed and OK. `M0` = not armed. `M2` = failsafe: stop and start again.

**RViz.** Only after the stack is up. Several laptops can view at once:

```bash
scripts/car.sh viz
```

If RViz says "no tf data", the bridge started before the car's: Ctrl-C and run it again.
Closing RViz never affects the car.

**Stop:**

```bash
scripts/car.sh stop
```

- Car e-stop first if it's moving. `stop` needs ssh: if the laptop has lost the hotspot, the
  e-stop is the only way to stop the kart.
- **After any trip (e-stop or failsafe) the kart never re-arms by itself:** `stop`, then
  `start` again.

**Live console on the Jetson** (optional): `scripts/car.sh attach`. Leave with `Ctrl-b d`;
**Ctrl-C there stops the stack.**

## Progress so far (2026-10-14)

- **Working:**
  - Stanley steering drives the servo through the Arduino ECU.
  - Auto-arm plus constant throttle works reliably on the kart.
  - RViz over zenoh shows the Stanley steering (wheels, arc, label).
- **Highest setting tested:** `throttle:=12` in no-pad mode (12 % throttle; `nopad_throttle_percent:=12` at the time). The real speed
  hasn't been measured yet: record `/zed/zed_node/odom` in a bag to get it.
- **Tight corners:** the camera loses sight of the cones, so Stanley has no path (`NOPATH`). The
  throttle cuts to 0 and steering centres, so the kart coasts straight on through the corner.
  This limits corner speed; the fix is better perception range or keeping the last path
  longer.
- **No pad:** the PS4 pad wouldn't connect, so this runs in no-pad mode (no deadman). The
  e-stop is the only stop.
- **Measured:** `stanley_sign` = +1 (+S steers right; the firmware comment saying left is
  wrong).
- **Not yet measured or tuned:**
  - `stanley_scale_left/right` (6.0 in `config/kart.yaml` is a guess that works);
  - `stanley_gain` 1.5 and `target_velocity` 1.5;
  - `front_axle_dist` (1.0 m guess; the camera and LiDAR mounts moved);
  - wheelbase.
- **Known issues:**
  - The LiDAR Ethernet dropped once (no path until reconnected).
  - The ECU tripped its 200 ms command watchdog once (`F1`) without a clear cause.
