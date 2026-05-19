# Design

## Overview

`VMWorkstationClient` is a small CLI-shaped client built on `ICommandRunner`. It
provides typed wrappers around the relevant `vmrun` subcommands for VM lifecycle,
snapshot lifecycle, guest exec, and inventory. Output parsing is pure Python; no
external dependencies beyond `automojo-interfaces`.

The client is deliberately scoped narrower than `automojo-interop-vsphere`:
Workstation is a developer / lab tool, not a primary provisioning venue. The
surface area covers what automojo workflows actually use against Workstation hosts,
and stops there.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│   Caller (landscaping, ad-hoc script, test harness)      │
└─────────────────────┬────────────────────────────────────┘
                      │ constructs & injects runner
                      ▼
┌──────────────────────────────────────────────────────────┐
│   VMWorkstationClient                                    │
│                                                          │
│   Lifecycle:  start, stop, suspend, reset                │
│   Snapshots:  snapshot_create/revert/delete/list         │
│   Guest exec: run_program_in_guest, copy_file_*,         │
│               tools_state                                │
│   Inventory:  list_running                               │
└─────────────────────┬────────────────────────────────────┘
                      │ delegates to
                      ▼
┌──────────────────────────────────────────────────────────┐
│   ICommandRunner (automojo-interfaces)                   │
└──────────┬─────────────────────────┬─────────────────────┘
           ▼                         ▼
┌─────────────────────┐    ┌─────────────────────┐
│ LocalCommandRunner  │    │ SSHCommandRunner    │
└─────────────────────┘    └─────────────────────┘
```

---

## Data Model

```python
class VMWorkstationActionStatus(Enum):
    SUCCESS = "success"
    FAILED  = "failed"
    DRY_RUN = "dry_run"


@dataclass
class VMWorkstationActionResult:
    status: VMWorkstationActionStatus
    detail: Optional[str]
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    command: Optional[List[str]]


class ToolsState(Enum):
    INSTALLED     = "installed"
    RUNNING       = "running"
    NOT_INSTALLED = "not_installed"
    UNKNOWN       = "unknown"


@dataclass
class SnapshotRecord:
    name: str
    parent: Optional[str]


@dataclass
class GuestExecResult:
    status: VMWorkstationActionStatus
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]


class VMWorkstationParseError(Exception):
    """Raised when vmrun output cannot be parsed."""


@dataclass
class GuestCredential:
    username: str
    password: str
```

---

## Command Mapping

| Operation | `vmrun` invocation |
| --- | --- |
| start | `vmrun -T <host_type> start <vmx> <gui|nogui>` |
| stop | `vmrun -T <host_type> stop <vmx> <soft|hard>` |
| suspend | `vmrun -T <host_type> suspend <vmx>` |
| reset | `vmrun -T <host_type> reset <vmx> <soft|hard>` |
| snapshot_create | `vmrun -T <host_type> snapshot <vmx> <name>` |
| snapshot_revert | `vmrun -T <host_type> revertToSnapshot <vmx> <name>` |
| snapshot_delete | `vmrun -T <host_type> deleteSnapshot <vmx> <name>` |
| snapshot_list | `vmrun -T <host_type> listSnapshots <vmx>` |
| run_program_in_guest | `vmrun -T <host_type> -gu <user> -gp <pw> runProgramInGuest <vmx> [-noWait] [-activeWindow] <program> [args...]` |
| copy_file_to_guest | `vmrun -T <host_type> -gu <user> -gp <pw> copyFileFromHostToGuest <vmx> <src> <dst>` |
| copy_file_from_guest | `vmrun -T <host_type> -gu <user> -gp <pw> copyFileFromGuestToHost <vmx> <src> <dst>` |
| tools_state | `vmrun -T <host_type> checkToolsState <vmx>` |
| list_running | `vmrun -T <host_type> list` |

---

## Module Layout

```
source/packages/automojo/interop/vmworkstation/
├── __init__.py
├── vmworkstationclient.py      # VMWorkstationClient + config
├── results.py                  # VMWorkstationActionResult, GuestExecResult, etc.
├── snapshots.py                # SnapshotRecord + list parser
├── guestcredential.py          # GuestCredential
└── aspectsvmworkstation.py     # DEFAULT_VMWORKSTATION_ASPECTS
```

---

## See Also

- `automojo-interfaces.icommandrunner` — the transport contract.
- `automojo-interop-vsphere` — the sibling REST-shaped client for vCenter; deliberately
  separate because the protocols are unrelated.

---

## Testing Strategy

- All tests use a `MockCommandRunner` keyed on `vmrun` argv prefix.
- Lifecycle, snapshot, guest-exec, inventory methods each have:
  - happy-path test asserting the exact argv constructed
  - failure-path test (non-zero exit) asserting `status=FAILED` and stderr capture
  - dry-run test asserting the runner is not invoked and `status=DRY_RUN`
- Parser tests for `listSnapshots` and `list` outputs use representative captured
  outputs as fixtures.
- No live Workstation install required.
