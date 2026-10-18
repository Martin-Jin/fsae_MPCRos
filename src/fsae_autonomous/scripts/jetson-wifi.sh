#!/usr/bin/env bash
# Run ON THE JETSON: join a Wi-Fi hotspot (phone, laptop, router) and keep a fixed address on it.
#
# Usage:
#   ./jetson-wifi.sh                         # prompts for hotspot name and password
#   ./jetson-wifi.sh "MyPhone" "password"
#   ./jetson-wifi.sh "MyPhone" --pin 192.168.43.50   # choose the fixed address yourself
#   ./jetson-wifi.sh "MyPhone" --no-pin              # DHCP only, no fixed address
#   ./jetson-wifi.sh "MyPhone" --hidden              # hotspot does not broadcast its name
#   ./jetson-wifi.sh "MyPhone" --country AU          # Wi-Fi country (default NZ, or $WIFI_COUNTRY)
#   ./jetson-wifi.sh --status                        # show current Wi-Fi addresses
#
# From the laptop over USB-C, copy it across and run it inside tmux, so a dropped link does
# not kill it halfway (rerun the ssh line to reattach; `exit` closes it when done):
#   scp scripts/jetson-wifi.sh fsae@192.168.55.1:/tmp/
#   ssh -t fsae@192.168.55.1 "tmux new -A -s wifi 'bash /tmp/jetson-wifi.sh FSAE-Kart; exec bash'"
#
# Before scanning it sets the Wi-Fi country (NZ by default) and makes it permanent. With no
# country set ("00") the radio scans several channels passively only and can miss a hotspot
# that a phone sees.
#
# What it sets up (saved by NetworkManager, survives reboots):
#   - Wi-Fi country, in /etc/modprobe.d/fsae-wifi-country.conf
#   - autoconnect to this hotspot at boot and whenever it comes back in range
#   - priority 150, above the Jetson's own "Hotspot" AP profile (100) if one exists, so the
#     Jetson joins this network when it is visible and falls back to its own AP otherwise
#   - DHCP as normal, PLUS a fixed extra address in the same subnet ("pin"), so the SSH
#     address stays the same across reconnects. If the hotspot ever moves to a different
#     subnet the pin stops working but DHCP still does; rerun this script to re-pin.
#
# Run it over the USB-C link (ssh fsae@192.168.55.1): switching Wi-Fi drops any SSH
# session that is itself running over Wi-Fi.
set -euo pipefail

SSID=""; PASSWORD=""; PIN="auto"; HIDDEN="no"; PRIORITY=150
COUNTRY="${WIFI_COUNTRY:-NZ}"
ORIG_ARGS=("$@")

log()  { printf '\033[1;34m[wifi]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[wifi]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[wifi]\033[0m %s\n' "$*" >&2; exit 1; }

command -v nmcli >/dev/null || die "nmcli (NetworkManager) not found"

wifi_iface() { nmcli -t -f DEVICE,TYPE device | awk -F: '$2=="wifi"{print $1; exit}'; }

show_status() {
    local ifc; ifc="$(wifi_iface)"
    [[ -n "$ifc" ]] || die "no Wi-Fi interface found (nmcli device)"
    log "interface $ifc: $(nmcli -t -f GENERAL.STATE,GENERAL.CONNECTION device show "$ifc" | cut -d: -f2 | paste -sd' ')"
    ip -4 -o addr show "$ifc" | awk '{print "  " $4}'
    log "hostname: $(hostname).local"
}

POSITIONAL=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --pin)    PIN="$2"; shift 2 ;;
        --no-pin) PIN="none"; shift ;;
        --hidden) HIDDEN="yes"; shift ;;
        --country) COUNTRY="$2"; shift 2 ;;
        --status) show_status; exit 0 ;;
        -h|--help) sed -n '2,32p' "$0"; exit 0 ;;
        -*) die "unknown option: $1" ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done
SSID="${POSITIONAL[0]:-}"
PASSWORD="${POSITIONAL[1]:-}"

# Over SSH outside tmux, a dropped link kills the script mid-switch. Warn (not fatal).
if [[ $EUID -ne 0 && -n "${SSH_CONNECTION:-}" && -z "${TMUX:-}" ]]; then
    warn "not inside tmux: if this SSH link drops, the script dies with it. Safer:"
    warn "  tmux new -A -s wifi 'bash $0 ${ORIG_ARGS[*]}; exec bash'"
fi

# nmcli needs root to change system connections from an SSH session (polkit denies it,
# which also means an unprivileged `nmcli device wifi rescan` silently returns stale results).
if [[ $EUID -ne 0 ]]; then
    # bash "$0": works when started as `bash jetson-wifi.sh` (no exec bit, or no ./ for
    # sudo's PATH lookup). SSH_CONNECTION is kept so the over-Wi-Fi warning below still
    # fires; sudo's env_reset would otherwise drop it.
    exec sudo --preserve-env=SSH_CONNECTION -- bash "$0" "${ORIG_ARGS[@]}"
fi

[[ -n "$SSID" ]] || read -r -p "Hotspot name (SSID): " SSID
[[ -n "$SSID" ]] || die "no hotspot name given"
if [[ -z "$PASSWORD" ]]; then
    read -r -s -p "Password for '$SSID' (empty for an open network): " PASSWORD; echo
fi
[[ -z "$PASSWORD" || ${#PASSWORD} -ge 8 ]] || die "WPA passwords are at least 8 characters"

IFACE="$(wifi_iface)"
[[ -n "$IFACE" ]] || die "no Wi-Fi interface found (nmcli device)"
CON="wifi-$SSID"

if [[ -n "${SSH_CONNECTION:-}" ]]; then
    server_ip="$(awk '{print $3}' <<<"$SSH_CONNECTION")"
    if [[ "$(ip -4 -o addr show "$IFACE")" == *" $server_ip/"* ]]; then
        warn "this SSH session is running over $IFACE; it will drop when the network switches."
        warn "Prefer running this over USB-C (ssh fsae@192.168.55.1). Continuing in 5 s, Ctrl-c to stop."
        sleep 5
    fi
fi

# With no country the radio only scans some channels passively and can miss the hotspot
# (seen with a Windows Mobile Hotspot on channel 11). Set it now and on every boot.
if command -v iw >/dev/null; then
    if ! iw reg get 2>/dev/null | grep -q "country $COUNTRY:"; then
        log "setting Wi-Fi country to $COUNTRY"
        iw reg set "$COUNTRY" || warn "iw reg set $COUNTRY failed"
        sleep 2
    fi
    echo "options cfg80211 ieee80211_regdom=$COUNTRY" > /etc/modprobe.d/fsae-wifi-country.conf
else
    warn "iw not installed; Wi-Fi country left as is"
fi

# Lines are captured before matching: `cmd | grep -q` can report a miss under pipefail
# when grep exits early and the writer gets SIGPIPE.
has_line() { grep -Fxq -- "$1" <<<"$2"; }

log "turning Wi-Fi on and scanning on $IFACE"
nmcli radio wifi on
visible="no"
for attempt in 1 2 3; do
    nmcli device wifi rescan ifname "$IFACE" 2>/dev/null || true
    sleep 5
    if has_line "$SSID" "$(nmcli -t -f SSID device wifi list ifname "$IFACE")"; then
        visible="yes"; break
    fi
    [[ $attempt -lt 3 ]] && log "'$SSID' not seen yet, scanning again ($attempt/3)"
done
if [[ "$HIDDEN" == no && "$visible" == no ]]; then
    warn "'$SSID' not visible in the scan. Visible networks:"
    nmcli -f SSID,CHAN,SIGNAL,SECURITY device wifi list ifname "$IFACE" | head -20 >&2
    die "check the name (case-sensitive) and that the hotspot is on (Windows Mobile Hotspot: Band 2.4 GHz), or use --hidden"
fi

# Recreate the profile so a changed password or a stale pin never lingers.
if has_line "$CON" "$(nmcli -t -f NAME connection show)"; then
    nmcli connection delete "$CON" >/dev/null
fi

log "connecting to '$SSID'"
connect_args=(device wifi connect "$SSID" ifname "$IFACE" name "$CON")
[[ -n "$PASSWORD" ]] && connect_args+=(password "$PASSWORD")
[[ "$HIDDEN" == yes ]] && connect_args+=(hidden yes)
nmcli "${connect_args[@]}" >/dev/null || die "connection failed (wrong password? hotspot full?)"

nmcli connection modify "$CON" connection.autoconnect yes connection.autoconnect-priority "$PRIORITY"

DHCP_CIDR=""
for _ in $(seq 1 15); do
    DHCP_CIDR="$(ip -4 -o addr show "$IFACE" | awk '{print $4}' | head -n1)"
    [[ -n "$DHCP_CIDR" ]] && break
    sleep 1
done
[[ -n "$DHCP_CIDR" ]] || die "connected but got no IP from the hotspot"
log "hotspot gave DHCP address $DHCP_CIDR"

if [[ "$PIN" != none ]]; then
    # Default pin: second-to-last usable host in the subnet (.253 on a /24, .13 on an
    # iPhone /28). Hotspot DHCP pools hand out from the bottom, so this rarely collides.
    PIN_CIDR="$(python3 - "$DHCP_CIDR" "$PIN" <<'EOF'
import ipaddress, sys
net = ipaddress.ip_interface(sys.argv[1]).network
want = sys.argv[2]
if want == "auto":
    hosts = list(net.hosts())
    addr = hosts[-2] if len(hosts) >= 3 else hosts[-1]
else:
    addr = ipaddress.ip_address(want)
    if addr not in net:
        sys.exit(f"--pin {addr} is not inside the hotspot subnet {net}")
print(f"{addr}/{net.prefixlen}")
EOF
)" || die "could not work out a fixed address"
    PIN_IP="${PIN_CIDR%/*}"
    if [[ "$PIN_CIDR" != "$DHCP_CIDR" ]] && ping -c 1 -W 1 "$PIN_IP" >/dev/null 2>&1; then
        warn "$PIN_IP already answers on this network; pick another with --pin"
        PIN_IP=""
    else
        nmcli connection modify "$CON" ipv4.method auto ipv4.addresses "$PIN_CIDR"
        nmcli connection up "$CON" >/dev/null
        log "fixed address $PIN_CIDR added (DHCP still active alongside it)"
    fi
fi

if [[ "$(nmcli -t -f NAME,802-11-wireless.mode,connection.autoconnect connection show 2>/dev/null || true)" == *":ap:yes"* ]]; then
    log "the Jetson's own AP profile also autoconnects; it is the fallback when '$SSID' is out of range"
fi

echo
show_status
echo
log "from a laptop on '$SSID':"
[[ -n "${PIN_IP:-}" ]] && log "  ssh $(logname 2>/dev/null || echo fsae)@$PIN_IP     (fixed)"
log "  ssh $(logname 2>/dev/null || echo fsae)@${DHCP_CIDR%/*}     (current DHCP, can change)"
log "  ssh $(logname 2>/dev/null || echo fsae)@$(hostname).local   (mDNS, PowerShell/Linux; usually not WSL)"
log "for car.sh (fsae_autonomous scripts/), on the laptop:"
log "  export FSAE_JETSON=$(logname 2>/dev/null || echo fsae)@${PIN_IP:-${DHCP_CIDR%/*}}"
