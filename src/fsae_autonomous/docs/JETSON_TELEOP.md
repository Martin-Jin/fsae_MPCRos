# Go Kart Tele-Op: Connecting to the Jetson and Driving

Two scripts in `scripts/` handle the connection, and the ROS 2 teleop launch drives the kart.

| Script | Runs on | Job |
| --- | --- | --- |
| [`jetson-connect.sh`](../scripts/jetson-connect.sh) | Laptop (WSL2 or Linux) | Brings up the USB-C link to the Jetson and SSHes in. With `--teleop`, also checks the gamepad and opens a ready-to-go tmux session |
| [`jetson-wifi.sh`](../scripts/jetson-wifi.sh) | Jetson | Joins a Wi-Fi hotspot once, with a fixed IP, so later sessions can SSH over Wi-Fi with no cable |

## Quick start

From the repo root on the laptop, with the USB-C cable plugged in and the Jetson booted:

```bash
scripts/jetson-connect.sh --teleop
```

1. Approve the prompts: `sudo` password (WSL), UAC on the very first run, Jetson SSH password.
2. Press PS on the pad if the script asks.
3. In tmux window 0, press **Enter** to run the teleop launch (it is typed, not started).
4. Do the [go handshake](#go-handshake) and drive, holding **X** throughout.

## `jetson-connect.sh`: USB-C link and SSH in one command

### Usage

```bash
scripts/jetson-connect.sh                 # connect and open an SSH shell
scripts/jetson-connect.sh --teleop        # connect, check the pad, open the tmux teleop session
scripts/jetson-connect.sh --link-only     # bring the link up only, no SSH
scripts/jetson-connect.sh -u jetson       # different Jetson username (default fsae)
scripts/jetson-connect.sh --teleop --pad-mac AA:BB:CC:DD:EE:FF   # different PS4 pad
scripts/jetson-connect.sh --ip <wifi-ip>  # Jetson already on Wi-Fi: no USB-C steps, just SSH
scripts/jetson-connect.sh --detach        # WSL2: give the cable back to Windows (PowerShell)
scripts/jetson-connect.sh --via-windows   # WSL2: use Windows' own USB adapter if it answers
```

`JETSON_USER`, `JETSON_IP` and `PAD_MAC` can also be set as environment variables. The script prints `export FSAE_JETSON=...` for `scripts/car.sh`.

### How it works

The Jetson's USB-C port acts as a USB network adapter, with the Jetson at `192.168.55.1`. On WSL2 that adapter is invisible until Windows passes the USB device through with `usbipd-win`, which the script drives through `powershell.exe`.

On WSL2 the script always attaches the Jetson to WSL, even when `192.168.55.1` already answers through Windows. The Windows route drops connections mid-command: Windows shows the cable as two adapters (Remote NDIS and UsbNcm) that swap the `192.168.55.100` lease, and a running Windows Mobile Hotspot makes it drop too. While attached to WSL, PowerShell cannot reach the Jetson over the cable; `--detach` gives it back.

| Step | What the script does |
| --- | --- |
| 1. Already reachable? | A Wi-Fi address (not `192.168.55.x`) is only pinged, then SSH. On native Linux, or WSL2 with `--via-windows`, a reachable `192.168.55.1` skips straight to SSH |
| 2. Find the Jetson (WSL only) | Reads `usbipd list` and picks the device with NVIDIA's USB vendor ID `0955` or "Remote NDIS" in its name, so the BUSID can differ by port or laptop. Waits up to 30 s for it to appear |
| 3. Bind (WSL only, first time) | If the device is "Not shared", runs `usbipd bind` elevated: one UAC prompt, remembered across reboots |
| 4. Attach (WSL only) | Runs `usbipd attach --wsl` (falls back to the older `usbipd wsl attach`). If Windows says "Attached" but WSL has no interface, detaches and re-attaches |
| 5. Find the interface | Looks for the network interface whose driver is `rndis_host` / `cdc_ether` / `cdc_ncm`, rather than a fixed `enx...` name, which changes per board |
| 6. Bring it up | `ip link set up`, then DHCP via `dhclient` or `dhcpcd`. If no lease arrives, sets `192.168.55.100/24` by hand |
| 7. Verify and SSH | Pings the Jetson for up to 10 s, then `ssh fsae@192.168.55.1` |

On native Linux, steps 2 to 4 are skipped. Every failure ends with a message naming the step that failed.

### `--teleop`: gamepad check and tmux session

After SSHing in, the script runs a check on the Jetson before opening tmux:

| Pad state | Action |
| --- | --- |
| `/dev/input/js*` exists (wired or already connected) | Continue |
| Bluetooth adapter off | `bluetoothctl power on` |
| Paired but not trusted | `bluetoothctl trust`, so it reconnects on its own next time |
| Paired, not connected | Asks for the PS button, retries `bluetoothctl connect`, waits up to 20 s |
| Connected but no `js*` | Suggests the driver fix (`sudo modprobe hid-sony`) |
| Never paired | Prints the one-time pairing steps (below) |
| Pad is not `js0` | Warns, since `teleop.launch.py` reads device 0 |

If the check fails it waits for Enter and opens tmux anyway, so the problem can be fixed by hand.

Then it attaches the existing `teleop` tmux session, or creates one:

| Window | Contents |
| --- | --- |
| 0 | ROS sourced, `js*` and serial device listed, `ros2 launch fsae_bringup teleop.launch.py` **typed, not run** |
| 1 | ROS sourced, `ros2 topic echo /fsae/control/actuator_cmd` typed, not run |

Nothing moves until Enter is pressed in window 0.

### Prerequisites

- A USB-C cable that carries data (charge-only cables give no adapter).
- The Jetson powered from its own supply.
- WSL2 only: `usbipd-win` installed on Windows (`winget install usbipd` in an Administrator PowerShell).
- One-time pad pairing on the Jetson. Hold Share and PS until the light bar flashes fast, then:

```bash
bluetoothctl
  scan on
  pair AC:FD:93:79:A5:7F
  trust AC:FD:93:79:A5:7F
  connect AC:FD:93:79:A5:7F
```

## `jetson-wifi.sh`: SSH over Wi-Fi with a fixed IP

### Usage

Run on the Jetson, over the USB-C link (switching Wi-Fi drops any SSH session that is itself on Wi-Fi):

```bash
./jetson-wifi.sh                                  # prompts for hotspot name and password
./jetson-wifi.sh "MyPhone" "password"
./jetson-wifi.sh "MyPhone" --pin 192.168.43.50    # choose the fixed IP
./jetson-wifi.sh "MyPhone" --no-pin               # DHCP only
./jetson-wifi.sh "MyPhone" --hidden               # hotspot does not broadcast its name
./jetson-wifi.sh "MyPhone" --country AU         # Wi-Fi country (default NZ, or $WIFI_COUNTRY)
./jetson-wifi.sh --status                         # show current Wi-Fi addresses
```

Copy it across from the laptop over USB-C, then run it inside tmux so a dropped link does not kill it halfway. Rerun the `ssh` line to reattach; type `exit` when it has finished.

```bash
scp scripts/jetson-wifi.sh fsae@192.168.55.1:/tmp/
ssh -t fsae@192.168.55.1 "tmux new -A -s wifi 'bash /tmp/jetson-wifi.sh FSAE-Kart; exec bash'"
```

It works whether started as `./jetson-wifi.sh` or `bash jetson-wifi.sh`, and warns when it is not inside tmux.

After setup, each session is: hotspot on, Jetson powered, laptop on the same hotspot, then `ssh fsae@<fixed-ip>` from PowerShell or WSL. The script also prints `export FSAE_JETSON=fsae@<fixed-ip>` for `scripts/car.sh` (see [GOKART_TEST_QUICKSTART.md](GOKART_TEST_QUICKSTART.md)), and `scripts/jetson-connect.sh --ip <fixed-ip>` connects over Wi-Fi the same way, skipping the USB-C steps. Rerun the script only when the hotspot name or password changes.

### How it works

| Step | What the script does |
| --- | --- |
| 1. Elevate | Re-runs itself with `sudo`, since NetworkManager refuses changes from an SSH session otherwise. Without root, `nmcli device wifi rescan` is refused and `nmcli device wifi list` returns a stale list |
| 2. Country | Sets the Wi-Fi country (`iw reg set NZ`) and writes `/etc/modprobe.d/fsae-wifi-country.conf` so it survives reboots. With no country (`00`) the Jetson did not see a Windows hotspot that a phone could see |
| 3. Scan | Turns Wi-Fi on and scans up to three times, 5 s apart. If the hotspot is still not visible, lists the networks it can see |
| 4. Connect | Creates a fresh saved profile `wifi-<name>` (replacing any old one, so a changed password never lingers) |
| 5. Autoconnect | Sets autoconnect, priority 150, so the Jetson rejoins at boot and whenever the hotspot is in range |
| 6. Fixed IP | Keeps the hotspot's DHCP address and adds a second, fixed address in the same subnet |
| 7. Report | Prints the fixed IP, the current DHCP IP and `fsae-desktop.local`, with ready-to-copy SSH commands |

### Why a fixed IP is added, not set

A hotspot hands out addresses by DHCP, and the address can change on every reconnect. A fully static IP would break outright if the hotspot ever moved to a different subnet. Adding a fixed address alongside DHCP keeps both working:

- The fixed address defaults to the second-to-last host in the subnet (`.253` on a `/24`, `.13` on an iPhone `/28`). Hotspots hand out addresses from the bottom, so this rarely collides.
- Before adding it, the script pings it and refuses if something already answers.

| Hotspot | Subnet | Fixed IP |
| --- | --- | --- |
| iPhone | always `172.20.10.0/28` | stays the same |
| Windows Mobile Hotspot | always `192.168.137.0/24` | stays the same |
| Android | usually stable, newer versions can change it | if it changes, the fixed IP stops working but DHCP still does. Run `--status` over USB-C, or rerun the script |

`ssh fsae@fsae-desktop.local` (mDNS) usually works from PowerShell but not from WSL.

If the Jetson also has its own AP profile ("Hotspot", priority 100) set to autoconnect, it becomes the fallback: the Jetson joins the phone hotspot when it is in range and starts its own AP otherwise.

## Driving

Teleop runs as ROS 2 nodes from the `fsae_autonomous` repo, branch `feat/SLAM` (which includes `feat/teleop-node-ground-testing`); `test/planning-teleop-ground-test` also contains it. `--teleop` refuses to start while the `car.sh` stack is running (tmux session `fsae`), since both drive the ECU serial port. The Jetson runs ROS 2 **Humble** (`/opt/ros/humble`), workspace `~/ros2_ws`.

| Node | Job |
| --- | --- |
| `joy_node` | Reads the pad from `/dev/input/js0`, publishes `/joy`. Picks the pad up again after a reconnect |
| `joystick_teleop` | Maps `/joy` to steer/throttle/brake, publishes `/fsae/control/actuator_cmd` |
| `serial_bridge` | Sends `S<steer> T<throttle> B<brake>` frames to the ECU over the FTDI USB serial adapter |

None of the nodes connect Bluetooth; that is BlueZ, plus the `--teleop` check above.

### Build (first time, or after pulling changes)

```bash
cd ~/ros2_ws/src/fsae_autonomous
git fetch origin && git checkout feat/SLAM && git pull
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select fsae_interfaces fsae_can_bridge fsae_serial_bridge fsae_bringup
source install/setup.bash
```

- Rebuild `fsae_interfaces` whenever `ActuatorCmd.msg` changes.
- An `already built in one or more underlay workspaces` warning is harmless.
- If `joy` is missing: `sudo apt install ros-humble-joy`.

### Controls

**X (Cross) must be held the whole time.** It is the deadman.

| Input | Action |
| --- | --- |
| X, held | Deadman. Released = neutral frames (steer 0, throttle 0, brake 0), kart coasts |
| Left stick, left/right | Steering |
| R2 | Throttle, full squeeze = 20% |
| L2 | Brake, full squeeze = 100%. Only works while X is held |

### Go handshake

Needed at ECU boot and after any trip, including a pad dropout.

1. Hold **X** and squeeze **L2** fully.
2. Keep the stick centred and R2 fully released.
3. Hold for 3 s until the ECU prints `READY`.
4. Release **L2** only, keep holding X. The ECU prints `GO`.

Stick drift under 5% is ignored, but a touched R2 or an off-centre stick blocks the handshake.

### Stops and failsafes

| Event | Result |
| --- | --- |
| X released | Soft stop: neutral frames keep flowing, kart coasts, ECU stays live |
| Pad lost (no `/joy` for 0.25 s) or teleop node dies | Hard stop: frames stop, ECU 1 s watchdog cuts HV and applies the brake |
| `Ctrl-c` in window 0 | Same as pad lost |

Do the first run with the wheels off the ground or the motor disconnected.

### Adjusting

```bash
ros2 topic echo /joy                                  # find axis/button indices on a different pad
ros2 param set /joystick_teleop invert_steer false    # if left/right are reversed
```

Permanent changes (throttle cap, button map, steering inversion) go in the `joystick_teleop:` block of `common/fsae_bringup/config/fsae_params.yaml`, then rebuild `fsae_bringup` and relaunch.

### tmux keys

| Keys | Action |
| --- | --- |
| `Ctrl-b` then `c` | New window |
| `Ctrl-b` then `0` / `1` | Switch window |
| `Ctrl-b` then `d` | Detach, teleop keeps running |
| `tmux attach -t teleop` | Reattach |
| `tmux kill-session -t teleop` | Delete the session and everything in it |

Press `Ctrl-b`, let go, then the key. Typing `exit` or closing window 0 kills the launch.

## Manual fallback

If a script fails, these are the steps it automates.

**USB-C link (WSL2):**

```powershell
usbipd list                              # Administrator PowerShell; find the Jetson's BUSID
usbipd bind --busid <BUSID>              # first time only
usbipd attach --wsl --busid <BUSID>      # after every replug or reboot
```

```bash
ip link                                  # find the enx... interface
sudo ip link set <iface> up
sudo dhclient <iface>
ssh fsae@192.168.55.1
```

**Teleop:**

```bash
tmux new -s teleop
source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash
ls /dev/input/js* /dev/serial/by-id/     # js0 and the FTDI adapter must be listed
ros2 launch fsae_bringup teleop.launch.py
```

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| `jetson-connect.sh`: Jetson not found in `usbipd list` | Charge-only cable, Jetson not booted, or try another port |
| `jetson-connect.sh`: no USB network interface appeared | Re-run; if it persists, `usbipd detach` then re-run |
| `jetson-connect.sh`: interface up but no ping | Jetson still booting. Wait and re-run |
| `jetson-wifi.sh`: hotspot not visible | Name is case-sensitive; hotspot off; Wi-Fi country unset (the script now sets it); or use `--hidden` |
| SSH over the cable drops mid-command (Windows) | Windows shows two adapters for the cable. Use `scripts/jetson-connect.sh` from WSL (attaches via usbipd), or from PowerShell disable one: `Disable-NetAdapter -Name "<Remote NDIS adapter>"` (Administrator) |
| WSL cannot reach the Jetson on a Windows Mobile Hotspot (`192.168.137.x`) | WSL, in NAT or mirrored mode, does not reach clients of the Windows hotspot. PowerShell can. For `car.sh` from WSL, use a phone hotspot (or a Linux laptop's hotspot) that the laptop joins as a client |
| `ssh: hostname contains invalid characters` | `FSAE_JETSON` is not set in this terminal, or the command was run inside an SSH session on the Jetson. Run it on the laptop after `export FSAE_JETSON=fsae@<ip>` |
| Windows `scp` from `\\wsl.localhost\...`: `stat local ... Unknown error` | Windows OpenSSH cannot read WSL paths. Copy the file to a Windows folder first, or run `scp` from WSL |
| Phone hotspot shows the Jetson only as a MAC address | Get its IP over the cable: `ssh fsae@192.168.55.1 "ip -4 -br addr show wlP1p1s0"`. A ping sweep needs a long timeout: the Jetson's Wi-Fi took about 0.8 s to answer the first ping |
| Wi-Fi SSH stopped working | Hotspot changed subnet (Android). `jetson-wifi.sh --status` over USB-C, or rerun the script |
| `source /opt/ros/jazzy/setup.bash`: no such file | The Jetson runs Humble. Use `/opt/ros/humble/setup.bash` |
| No `/dev/input/js0`, or teleop logs `PAD LOST` | Pad asleep or disconnected. Press PS, or plug in by USB. Check `ls /dev/input/js*` for `js1` |
| `serial_bridge` permission denied | `sudo usermod -aG dialout $USER`, then log in again |
| Different FTDI adapter | Change `serial_bridge.port` in `fsae_params.yaml` |
| Launch misbehaves or Jetson sluggish | Stale teleop running. `tmux kill-session -t teleop` or `pkill -f teleop_nano.py` |
| `bash\r: No such file` running a script | Windows converted line endings. `sed -i 's/\r$//' docs/*.sh`, or add `*.sh text eol=lf` to `.gitattributes` |

The older standalone script `/home/fsae/repo/nano_teleop/teleop_nano.py` predates the ROS 2 nodes. Do not run it alongside the ROS 2 launch: both open the same serial port.
