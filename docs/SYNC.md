# Keeping this repo in sync with `fsae_autonomous` and the simulator repos

**This repo is the shareable record of controller work in `fsae_autonomous`, and the one place where how that work relates to the simulator repos is written down.** Everything under `src/fsae_autonomous/` is a byte-for-byte copy of the production workspace and follows production's rules. This file and the README sit outside that tree and may reference the simulator.

## Two kinds of content, two rules

| Location | What it is | May mention the simulator? |
|---|---|---|
| `src/fsae_autonomous/<path>` | exact copy of `fsae_autonomous/<path>` | **No.** Same rule as production: describe the car or kart, mark any sim-only value with the token `UNVERIFIED` |
| `README.md`, `docs/` (repo root) | notes on syncing and provenance | Yes |

A mirrored file must never be edited here to add sim context. Fix it in `fsae_autonomous` first, then copy it across.

## The repos involved

| Repo | Role | Pushed by |
|---|---|---|
| `fsae_autonomous` | production, runs on the car or kart | the user, or an agent only on an explicit ask |
| `fsae_MPCRos` (this repo) | pushable mirror of the `fsae_autonomous` files being worked on | routinely, after every `fsae_autonomous` edit |
| `fsae_planning` (inside the FSDS simulator checkout) | where the MPC is developed and live-tested in simulation | never by an agent, except one named feature branch on explicit ask |
| `fsae_MPCTest` | offline tuner, plus `fsds_simulator/`, the change ledger for `fsae_planning` | routinely |

Branch pairing: `fsae_autonomous` `main` maps to `main` here, and `feat/mpc_ground_test` maps to `mpc-ground-test`. The go-kart connection scripts (`scripts/jetson-connect.sh`, `scripts/jetson-wifi.sh`) and their doc (`docs/JETSON_TELEOP.md`) come from `fsae_autonomous` `test/planning-teleop-ground-test` and are backed up on `mpc-ground-test` here.

## Before and after any change to mirrored files

1. **Before:** pull `fsae_autonomous` and this repo, so neither copy is stale.
2. **Make the change** in `fsae_autonomous`.
3. **After:** `cmp` every file this repo tracks against the `fsae_autonomous` working tree, not only the files you think you touched. Earlier edits made between mirror pushes have been missed this way before.
4. Copy the changed files to the same relative path under `src/fsae_autonomous/`, commit, push.

## Checking which parameter value runs: `param_report`

**One read-only command shows, for every `MPCParams`/`NMPCParams` field, the value production would run, which layer it came from, and how it compares with the simulator side.** It lives in `fsae_MPCTest` because that is the only checkout with every repo side by side.

```bash
cd fsae_MPCTest
python3 -m tuner.tools.param_report --prod-launch nmpc_gokart   # resolve the kart launch file
python3 -m tuner.tools.param_report --prod-launch control --all
```

A `PROD` flag means production differs from the simulator's live value or the field exists on only one side. That is informational: production is maintained separately and may differ on purpose. `UNV` marks a production field whose source or YAML carries `UNVERIFIED`.

### Which layer wins depends on the launch file

| Production launch file | How `nmpc_controller` gets its parameters | Effective order, highest first |
|---|---|---|
| `control.launch.py` | YAML, then every field as a launch argument defaulting to the dataclass value | launch argument, dataclass default, YAML (**YAML entries for dataclass fields are dead**) |
| `nmpc_gokart.launch.py`, `nmpc_shadow.launch.py` | YAML, then a short literal dict | literal dict, YAML, dataclass default |

So the same YAML edit takes effect under `nmpc_gokart` and is silently ignored under `control.launch.py`. Keep the YAML and the dataclass default equal. The ordering was confirmed with a minimal `launch_ros` test: a later launch dict overrides an earlier YAML file.

## Pushing tuned parameter values from the simulator

`fsae_MPCTest`'s `tuner.tools.sync_mpc_params` copies `mpc_params.py`, `nmpc_params.py` and `fsae_params.yaml` one way from `fsae_planning` into the local `fsae_autonomous` working tree. **Do not run `--apply` blindly against production.** It overwrites whole files, including kart-specific and `UNVERIFIED` values. Run the dry run, compare against `param_report`, and carry over only the values meant for the car. Any value that arrives from the simulator gets an `UNVERIFIED` marker until measured on the hardware.
