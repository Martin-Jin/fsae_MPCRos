# CanTalk integration (PORTED - launch commented out)

`fsae_can_bridge` merges three old packages:

- `gocart_control`  -> ack_to_can, sys_status, mock_stimulus, joystick_teleop  (ported)
- `gocart_driver`   -> can_decoder_jnano, drivers/MCP2515.py                    (ported)
- **CanTalk**        -> the CAN hardware interface (`candapter.py`)             (**ported**)

## What it is

CanTalk was a git submodule (`github.com/UOA-FSAE/CanTalk`, `nightly` branch). It is the
node that actually talks to the CAN bus (a **CANdapter** USB-serial adapter) and bridges
hardware <-> ROS:

- subscribes outgoing frames     <- `/fsae/hardware/can_tx`  (produced by `ack_to_can`)  -> writes to the bus
- publishes raw received frames  -> `/fsae/hardware/can_rx`  (consumed by `can_decoder`)

Without it, `ack_to_can` and `can_decoder` have no hardware link (can_tx/can_rx go nowhere).

## How it was ported

Rather than re-add the submodule, the source was **vendored** as a module of this package
(`fsae_can_bridge/candapter.py`), copied from the old working tree at
`/home/fsae/autonomous/src/gocart/CanTalk/CanTalk/CanDapter.py` (which already carried the
uncommitted `moa_msgs -> fsae_interfaces` rename - upstream `nightly` still imports the
now-deleted `moa_msgs` and would NOT build). Changes made during the port:

- **TX/RX topic split.** The old node subscribed *and* published a single shared topic
  `can` (remapped to `pub_raw_can`); this repo split TX and RX, and one topic name cannot
  be remapped to two targets. So the code now uses `/fsae/hardware/can_tx` (sub) and
  `/fsae/hardware/can_rx` (pub) directly. The old `frame_id == 'CanDapter_node'`
  self-filter was dropped (only needed when sub and pub shared a topic).
- **Node renamed** `CanDapter_node` -> `candapter_node` to match the launch name + yaml key.
- **Light hardening:** the serial open is wrapped so a missing/wrong device logs and the
  node idles instead of crashing; the empty-serial-read `IndexError` is guarded. Behaviour
  is unchanged when the adapter is present.
- **No message changes** - `CANStamped`/`CAN` are byte-identical to what CanTalk expects.

Packaging wired up:

- `setup.py` console_scripts: `candapter_node = fsae_can_bridge.candapter:main`
- `package.xml`: `<exec_depend>python3-serial</exec_depend>` (pyserial); also in `requirements.txt`
- `fsae_params.yaml`: `candapter_node` block (`port`, `baud_rate`)

## To enable it (on the Jetson, adapter plugged in)

1. Uncomment the `candapter_node` `Node(...)` block in `can.launch.py` (it is left commented
   because it opens `/dev/ttyUSB0` and would error off-car).
2. Set the right `port` in `fsae_params.yaml` if not `/dev/ttyUSB0`.
3. `rosdep install` (pulls `python3-serial`) or `pip install pyserial`.
4. The **inbound** decode path is ready — `can_decoder` now starts (its `AckermannStamped`
   import was fixed → `AckermannDriveStamped`, see MIGRATION_BUGS.md). The **outbound** path
   (commands -> kart) works with candapter_node alone.

## Known unknowns / caveats (preserved from the original)

- **Serial line speed unverified.** `serial.Serial(port)` opens at pyserial's default
  (9600 bps) for the USB-serial line; `baud_rate` only sets the CAN bitrate (the `Sx`
  command). Confirm the CANdapter's required USB-serial speed against the physical adapter.
- **Does NOT restore `curr_vel` / `hardware_state` / `mission_status`** - those are separate
  MoTeC-decode paths, so the AS state machine stays blocked even with candapter_node running.
- Pre-existing robustness gaps left as-is: bare `except` in the read loop, `clean_can_frame`
  can raise on malformed frames, no serial reconnect.
- Confirm the full CAN ID map / DBC against `can_decoder`'s params in `fsae_params.yaml`.
