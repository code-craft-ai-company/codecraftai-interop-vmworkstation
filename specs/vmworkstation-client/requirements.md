# Requirements

## Introduction

The `vmworkstation-client` feature delivers `VMWorkstationClient`, the dedicated
client for driving VMware Workstation through the `vmrun` CLI. It replaces the
legacy `automojo-landscaping/services/vmware/vmworkstationagent.py`.

The client is built on `ICommandRunner` (from `automojo-interfaces`) — the same
abstraction firewall management, package management, and other CLI-shaped automojo
features use. This means the same `VMWorkstationClient` instance works:

- locally against a Workstation install on the same host (via `LocalCommandRunner`)
- remotely against a Workstation install on a different host (via `SSHCommandRunner`)

No REST, no native bindings — only `vmrun` invocations through the runner.

All public methods take `aspects: Aspects = DEFAULT_VMWORKSTATION_ASPECTS` for
behaviour control. No behaviour-modifying decorators.

---

## Requirements

### Requirement 1: Client Construction

#### Acceptance Criteria

1. WHEN the caller constructs `VMWorkstationClient(runner=ICommandRunner,
   vmrun_path=Optional[str], host_type=Literal["ws","fusion","player","server"])`
   THE SYSTEM SHALL store the runner, the resolved `vmrun` executable path
   (defaulting to `"vmrun"` if not supplied), and the host type.
2. WHEN construction succeeds THE SYSTEM SHALL NOT execute any command.

---

### Requirement 2: VM Lifecycle

**User Story:** As a caller, I want to start, stop, suspend, reset, and pause VMs.

#### Acceptance Criteria

1. WHEN `client.start(vmx_path=..., gui=False, aspects=...)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> start <vmx_path> nogui` (or `gui` when
   `gui=True`) and return a `VMWorkstationActionResult`.
2. WHEN `client.stop(vmx_path=..., hard=False, aspects=...)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> stop <vmx_path> <soft|hard>`.
3. WHEN `client.suspend(vmx_path=..., aspects=...)` is called THE SYSTEM SHALL
   invoke `vmrun -T <host_type> suspend <vmx_path>`.
4. WHEN `client.reset(vmx_path=..., hard=False, aspects=...)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> reset <vmx_path> <soft|hard>`.
5. WHEN any lifecycle command exits non-zero THE SYSTEM SHALL return a
   `VMWorkstationActionResult` with `status=FAILED`, the exit code, and the
   captured stderr.

---

### Requirement 3: Snapshot Lifecycle

#### Acceptance Criteria

1. WHEN `client.snapshot_create(vmx_path, name, aspects)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> snapshot <vmx_path> <name>`.
2. WHEN `client.snapshot_revert(vmx_path, name, aspects)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> revertToSnapshot <vmx_path> <name>`.
3. WHEN `client.snapshot_delete(vmx_path, name, aspects)` is called THE SYSTEM
   SHALL invoke `vmrun -T <host_type> deleteSnapshot <vmx_path> <name>`.
4. WHEN `client.snapshot_list(vmx_path, aspects)` is called THE SYSTEM SHALL
   invoke `vmrun -T <host_type> listSnapshots <vmx_path>` and parse the output
   into a `list[SnapshotRecord]`.

---

### Requirement 4: Guest Exec

#### Acceptance Criteria

1. WHEN `client.run_program_in_guest(vmx_path, guest_credential, program,
   args=None, no_wait=False, active_window=False, aspects=...)` is called THE
   SYSTEM SHALL invoke `vmrun runProgramInGuest` with the supplied options and
   return a `GuestExecResult`.
2. WHEN `client.copy_file_to_guest(vmx_path, guest_credential, source, target,
   aspects=...)` is called THE SYSTEM SHALL invoke `vmrun copyFileFromHostToGuest`.
3. WHEN `client.copy_file_from_guest(vmx_path, guest_credential, source, target,
   aspects=...)` is called THE SYSTEM SHALL invoke `vmrun copyFileFromGuestToHost`.
4. WHEN `client.tools_state(vmx_path, aspects)` is called THE SYSTEM SHALL invoke
   `vmrun checkToolsState <vmx_path>` and return one of
   `{INSTALLED, RUNNING, NOT_INSTALLED, UNKNOWN}`.

---

### Requirement 5: Inventory

#### Acceptance Criteria

1. WHEN `client.list_running(aspects)` is called THE SYSTEM SHALL invoke
   `vmrun -T <host_type> list` and return a `list[str]` of running VMX paths.
2. WHEN the parser cannot parse the output THE SYSTEM SHALL raise
   `VMWorkstationParseError` with the raw output attached.

---

### Requirement 6: Dry-Run Mode

#### Acceptance Criteria

1. WHEN the client is constructed with `dry_run=True` THE SYSTEM SHALL NOT invoke
   the runner for any write operation and SHALL return a
   `VMWorkstationActionResult` with `status=DRY_RUN`.
2. WHEN dry-run mode is active THE SYSTEM SHALL still execute read operations
   (`list_running`, `snapshot_list`, `tools_state`) — these are non-mutating.
