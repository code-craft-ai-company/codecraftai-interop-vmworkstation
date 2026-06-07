# Implementation Plan — VMWorkstation Client

- [x] 1. Create `ccai.interop.vmworkstation` package skeleton.

- [x] 2. Define result types and exceptions in `results.py` and `snapshots.py`.

- [x] 3. Define `GuestCredential` and `ToolsState` enum.

- [x] 4. Define `DEFAULT_VMWORKSTATION_ASPECTS` in `aspectsvmworkstation.py`.

- [x] 5. Implement `VMWorkstationClient.__init__(runner, vmrun_path, host_type,
  dry_run)`.

## Lifecycle methods

- [x] 6. `start(vmx_path, gui, aspects)`.
- [x] 7. `stop(vmx_path, hard, aspects)`.
- [x] 8. `suspend(vmx_path, aspects)`.
- [x] 9. `reset(vmx_path, hard, aspects)`.

## Snapshot methods

- [x] 10. `snapshot_create(vmx_path, name, aspects)`.
- [x] 11. `snapshot_revert(vmx_path, name, aspects)`.
- [x] 12. `snapshot_delete(vmx_path, name, aspects)`.
- [x] 13. `snapshot_list(vmx_path, aspects)` with output parser.

## Guest exec methods

- [x] 14. `run_program_in_guest(...)` with `no_wait` / `active_window` flags.
- [x] 15. `copy_file_to_guest(...)`.
- [x] 16. `copy_file_from_guest(...)`.
- [x] 17. `tools_state(vmx_path, aspects)`.

## Inventory

- [x] 18. `list_running(aspects)` with output parser.

## Cross-cutting

- [x] 19. Dry-run short-circuit on every write method.
- [x] 20. Helper `_dispatch(args, aspects)` that builds the argv prefix
  (`vmrun -T <host_type>`) and invokes the runner.

## Tests

- [x] 21. Happy-path argv tests per method.
- [x] 22. Failure-path tests (non-zero exit → `FAILED` + stderr).
- [x] 23. Dry-run tests per write method.
- [x] 24. Parser tests for `listSnapshots` and `list`.
- [x] 25. `tools_state` parsing for all four states.
