#!/usr/bin/env bash
# Connect to the Jetson over the USB-C cable and SSH in, from WSL2 or native Linux.
#
# Handles: usbipd not bound (asks for UAC once), not attached, attached but the
# interface lost, interface down, no DHCP lease, different BUSID / interface name.
#
# On WSL2 the Jetson is always attached to WSL with usbipd, even when 192.168.55.1 already
# answers through Windows' own USB adapter. That Windows route is unreliable: Windows
# shows the cable as two adapters (Remote NDIS and UsbNcm) that swap the 192.168.55.100
# lease, and a running Mobile Hotspot makes it drop too, killing SSH sessions mid-command.
# While attached to WSL, PowerShell cannot reach the Jetson over the cable (use --detach).
#
# Usage:
#   scripts/jetson-connect.sh                 # connect and open an SSH shell
#   scripts/jetson-connect.sh --teleop        # connect, then start/attach the tmux teleop session
#   scripts/jetson-connect.sh --link-only     # bring the link up, don't SSH
#   scripts/jetson-connect.sh -u jetson       # different Jetson username (default fsae)
#   scripts/jetson-connect.sh --teleop --pad-mac AA:BB:CC:DD:EE:FF   # different PS4 pad
#   scripts/jetson-connect.sh --ip 192.168.137.253   # Jetson over Wi-Fi (fixed IP from jetson-wifi.sh):
#                                                    # no USB-C steps for a non-192.168.55.x address
#   scripts/jetson-connect.sh --via-windows   # WSL: use Windows' own USB adapter if it answers
#   scripts/jetson-connect.sh --detach        # WSL: give the cable back to Windows (PowerShell)
#
# --teleop also checks the gamepad on the Jetson before opening tmux: powers Bluetooth on,
# trusts and connects the pad if needed, and waits for /dev/input/js*.
#
# Env overrides: JETSON_USER, JETSON_IP, PAD_MAC.
set -euo pipefail

JETSON_USER="${JETSON_USER:-fsae}"
JETSON_IP="${JETSON_IP:-192.168.55.1}"
HOST_IP="192.168.55.100/24"
PAD_MAC="${PAD_MAC:-AC:FD:93:79:A5:7F}"
MODE="ssh"
VIA_WINDOWS="no"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -u|--user)    JETSON_USER="$2"; shift 2 ;;
        --ip)         JETSON_IP="$2"; shift 2 ;;
        --teleop)     MODE="teleop"; shift ;;
        --link-only)  MODE="link"; shift ;;
        --via-windows) VIA_WINDOWS="yes"; shift ;;
        --detach)     MODE="detach"; shift ;;
        --pad-mac)    PAD_MAC="$2"; shift 2 ;;
        -h|--help)    sed -n '2,27p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

log()  { printf '\033[1;34m[jetson]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[jetson]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[jetson]\033[0m %s\n' "$*" >&2; exit 1; }

reachable() { ping -c 1 -W 1 "$JETSON_IP" >/dev/null 2>&1; }

is_wsl() { grep -qi microsoft /proc/version 2>/dev/null; }

# The USB-C link only ever serves 192.168.55.x; any other address is Wi-Fi.
is_usb_ip() { [[ "$JETSON_IP" == 192.168.55.* ]]; }

# The Jetson's USB gadget shows up as an RNDIS / CDC Ethernet device. Identify it by
# driver rather than by name, since the enx... name comes from a per-board MAC.
jetson_iface() {
    local dev drv
    for dev in /sys/class/net/*; do
        [[ -e "$dev/device/driver" ]] || continue
        drv="$(basename "$(readlink -f "$dev/device/driver")")"
        case "$drv" in
            rndis_host|cdc_ether|cdc_ncm|cdc_eem) basename "$dev"; return 0 ;;
        esac
    done
    # Fallback for kernels where the driver link is missing.
    # || true: with pipefail a grep miss would fail the caller's iface="$(jetson_iface)"
    # under set -e and kill the script on the first poll, before the interface appears.
    ip -o link | awk -F': ' '{print $2}' | grep -E '^(enx|usb)' | head -n1 || true
}

ps_run() { powershell.exe -NoProfile -NonInteractive -Command "$1" 2>/dev/null | tr -d '\r'; }

# Prints "BUSID|STATE" for the Jetson in `usbipd list`. Matches NVIDIA's VID (0955)
# or the RNDIS description, so a different port or BUSID doesn't matter.
find_jetson_busid() {
    ps_run "usbipd list" | awk '
        /^Persisted:/ { exit }
        /^[0-9]+-[0-9.]+[ \t]/ && (/0955:/ || /Remote NDIS/) {
            busid = $1
            if ($0 ~ /Not shared[ \t]*$/)      state = "Not shared"
            else if ($0 ~ /Attached[ \t]*$/)   state = "Attached"
            else                               state = "Shared"
            print busid "|" state
            exit
        }' || true
}

usbipd_attach() {
    local busid="$1"
    # usbipd-win 4+ syntax first, then the older `usbipd wsl attach`.
    ps_run "usbipd attach --wsl --busid $busid" >/dev/null \
        || ps_run "usbipd wsl attach --busid $busid" >/dev/null || true
}

wsl_passthrough() {
    command -v powershell.exe >/dev/null || die "powershell.exe not found from WSL (Windows interop disabled?)"
    # Captured first: `cmd | grep -q` can report a miss under pipefail when grep exits early.
    local have
    have="$(ps_run "Get-Command usbipd -ErrorAction SilentlyContinue")" || true
    [[ "$have" == *usbipd* ]] \
        || die "usbipd-win not installed. In an Administrator PowerShell: winget install usbipd"

    local entry="" i
    for i in $(seq 1 15); do
        entry="$(find_jetson_busid)"
        [[ -n "$entry" ]] && break
        [[ $i -eq 1 ]] && log "waiting for the Jetson to appear on Windows USB (check cable/power)..."
        sleep 2
    done
    [[ -n "$entry" ]] || die "Jetson not found in 'usbipd list'. Use a data USB-C cable, wait for boot, try another port."

    local busid="${entry%%|*}" state="${entry#*|}"
    log "Jetson on Windows BUSID $busid ($state)"

    if [[ "$state" == "Not shared" ]]; then
        log "binding BUSID $busid (one-time, approve the UAC prompt on Windows)"
        ps_run "Start-Process usbipd -ArgumentList 'bind','--busid','$busid' -Verb RunAs -Wait" >/dev/null || true
        state="$(find_jetson_busid | cut -d'|' -f2)"
        [[ "$state" != "Not shared" ]] || die "bind failed or UAC was declined"
    fi

    if [[ "$state" == "Attached" && -z "$(jetson_iface)" ]]; then
        warn "usbipd says attached but WSL has no interface; re-attaching"
        ps_run "usbipd detach --busid $busid" >/dev/null || true
        sleep 1
        state="Shared"
    fi

    if [[ "$state" != "Attached" ]]; then
        log "attaching BUSID $busid to WSL"
        usbipd_attach "$busid"
    fi
}

bring_up_link() {
    local iface="" i
    for i in $(seq 1 15); do
        iface="$(jetson_iface)"
        [[ -n "$iface" ]] && break
        sleep 1
    done
    [[ -n "$iface" ]] || die "no USB network interface appeared (ip link shows no enx.../usb...)"
    log "interface $iface"

    sudo ip link set "$iface" up

    if ! ip -4 addr show "$iface" | grep -q 'inet 192\.168\.55\.'; then
        log "requesting an IP from the Jetson (DHCP)"
        if command -v dhclient >/dev/null; then
            sudo timeout 15 dhclient -1 "$iface" || true
        elif command -v dhcpcd >/dev/null; then
            sudo timeout 15 dhcpcd -1 "$iface" || true
        fi
    fi
    if ! ip -4 addr show "$iface" | grep -q 'inet 192\.168\.55\.'; then
        warn "no DHCP lease, falling back to static $HOST_IP"
        sudo ip addr add "$HOST_IP" dev "$iface" 2>/dev/null || true
    fi
}

detach_link() {
    is_wsl || die "--detach is for WSL2 only"
    local entry; entry="$(find_jetson_busid)"
    [[ -n "$entry" ]] || die "Jetson not found in 'usbipd list'"
    ps_run "usbipd detach --busid ${entry%%|*}" >/dev/null || true
    log "BUSID ${entry%%|*} handed back to Windows; PowerShell can reach $JETSON_IP again"
}

connect_link() {
    if ! is_usb_ip; then
        # Wi-Fi address: nothing to bring up, just check it answers.
        reachable && { log "$JETSON_IP reachable over Wi-Fi"; return; }
        die "$JETSON_IP does not answer. Same hotspot as the Jetson? (WSL cannot reach clients of a Windows Mobile Hotspot)"
    fi
    if is_wsl && [[ "$VIA_WINDOWS" == no ]]; then
        # Skip the Windows route even if it answers (see the header); attach to WSL.
        [[ -n "$(jetson_iface)" ]] || wsl_passthrough
    elif reachable; then
        log "$JETSON_IP already reachable"
        return
    elif is_wsl; then
        wsl_passthrough
    fi
    bring_up_link

    local i
    for i in $(seq 1 10); do
        reachable && { log "$JETSON_IP reachable"; return; }
        sleep 1
    done
    die "interface is up but $JETSON_IP does not answer ping (Jetson still booting?)"
}

# Runs on the Jetson. $1 = pad MAC.
REMOTE_TELEOP=$(cat <<'EOF'
mac="$1"
pad() { printf "\033[1;34m[pad]\033[0m %s\n" "$*"; }
have_js() { ls /dev/input/js* >/dev/null 2>&1; }

# Bluetooth only matters when no joystick device exists; a wired pad passes straight through.
pad_check() {
    if have_js; then
        pad "joystick present: $(ls /dev/input/js* | tr "\n" " ")"
        return 0
    fi
    command -v bluetoothctl >/dev/null || { pad "no /dev/input/js* and bluetoothctl is not installed"; return 1; }

    if ! timeout 5 bluetoothctl show 2>/dev/null | grep -q "Powered: yes"; then
        pad "Bluetooth adapter is off, powering on"
        timeout 5 bluetoothctl power on >/dev/null 2>&1 || true
    fi

    local info
    info="$(timeout 5 bluetoothctl info "$mac" 2>/dev/null || true)"
    if ! grep -q "Paired: yes" <<<"$info"; then
        pad "$mac is not paired. One-time pairing: hold Share+PS until the light flashes fast, then run"
        pad "  bluetoothctl   then:  scan on / pair $mac / trust $mac / connect $mac"
        return 1
    fi
    if ! grep -q "Trusted: yes" <<<"$info"; then
        pad "trusting $mac so it reconnects by itself next time"
        timeout 5 bluetoothctl trust "$mac" >/dev/null 2>&1 || true
    fi
    grep -q "Connected: yes" <<<"$info" || pad "pad not connected: press the PS button on it now"

    local i
    for i in $(seq 1 20); do
        if have_js; then
            pad "connected: $(ls /dev/input/js* | tr "\n" " ")"
            return 0
        fi
        # A pad woken by PS reconnects itself; this host-side connect covers one that is
        # awake but not linked.
        if (( i % 5 == 1 )); then timeout 8 bluetoothctl connect "$mac" >/dev/null 2>&1 || true; fi
        sleep 1
    done
    if timeout 5 bluetoothctl info "$mac" 2>/dev/null | grep -q "Connected: yes"; then
        pad "Bluetooth says connected but no /dev/input/js* appeared (driver issue? try: sudo modprobe hid-sony)"
    else
        pad "pad did not connect. Check it is charged and on, or plug it in by USB"
    fi
    return 1
}

# car.sh runs the full stack in tmux session 'fsae'. Two stacks fight over the ECU serial
# port and the ZED, so refuse to start teleop next to it.
if tmux has-session -t fsae 2>/dev/null; then
    pad "the car.sh stack is running (tmux session 'fsae'). Stop it first: scripts/car.sh stop"
    exit 1
fi

if pad_check; then
    if [ ! -e /dev/input/js0 ]; then
        pad "warning: pad is not js0; teleop.launch.py reads device_id 0. Replug or reconnect until it is js0"
    fi
else
    read -r -p "[pad] press Enter to open tmux anyway (Ctrl-c to quit) " _
fi

# Attach the teleop session if it exists, otherwise create it with ROS sourced and the
# launch command typed but NOT run, so nothing moves until Enter is pressed.
if tmux has-session -t teleop 2>/dev/null; then
    exec tmux attach -t teleop
fi
tmux new-session -d -s teleop -c ~/ros2_ws
tmux send-keys -t teleop "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash && ls /dev/input/js* /dev/serial/by-id/" Enter
tmux send-keys -t teleop "ros2 launch fsae_bringup teleop.launch.py"
tmux new-window -t teleop -c ~/ros2_ws
tmux send-keys -t teleop:1 "source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash" Enter
tmux send-keys -t teleop:1 "ros2 topic echo /fsae/control/actuator_cmd"
tmux select-window -t teleop:0
exec tmux attach -t teleop
EOF
)

if [[ "$MODE" == detach ]]; then
    detach_link
    exit 0
fi

connect_link

TARGET="$JETSON_USER@$JETSON_IP"
# car.sh (fsae_autonomous scripts/) works over this link too.
log "for car.sh: export FSAE_JETSON=$TARGET"
case "$MODE" in
    link)
        log "link up. ssh $TARGET"
        ;;
    ssh)
        log "ssh $TARGET"
        exec ssh "$TARGET"
        ;;
    teleop)
        log "ssh $TARGET -> gamepad check, then tmux session 'teleop'"
        exec ssh -t "$TARGET" "bash -c $(printf '%q' "$REMOTE_TELEOP") teleop $(printf '%q' "$PAD_MAC")"
        ;;
esac
