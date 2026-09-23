"""
    .. module:: vmworkstationclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: :class:`VMWorkstationClient` — typed interop client for
                   VMware Workstation driven through the ``vmrun`` CLI.

    The client wraps the relevant ``vmrun`` subcommands for VM lifecycle,
    snapshot lifecycle, guest exec, and inventory. All command dispatch is
    routed through an injected :class:`ICommandRunner`, which means the same
    client class works locally (``LocalCommandRunner``) or remotely
    (``SSHCommandRunner``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import List, Optional

from ccai.interfaces.icommandrunner import ICommandRunner, RunResult

from ccai.interop.vmworkstation.aspectsvmworkstation import (
    AspectsVMWorkstation,
)
from ccai.interop.vmworkstation.exceptions import VMRunCommandError
from ccai.interop.vmworkstation.guestcredential import GuestCredential
from ccai.interop.vmworkstation.redaction import redact_argv
from ccai.interop.vmworkstation.results import (
    GuestExecResult,
    ToolsState,
    VMWorkstationActionResult,
    VMWorkstationActionStatus,
)
from ccai.interop.vmworkstation.snapshots import (
    SnapshotRecord,
    parse_list_running,
    parse_list_snapshots,
)
from ccai.interop.vmworkstation.vmrundispatcher import VMRunDispatcher


_DEFAULT_VMRUN_PATH = "vmrun"
_DEFAULT_HOST_TYPE = "ws"
_SUPPORTED_HOST_TYPES = ("ws", "fusion", "player", "server")


class VMWorkstationClient:
    """
        Typed client for VMware Workstation, driven through the ``vmrun``
        CLI dispatched via an :class:`ICommandRunner`.

        :param runner: The injected command runner.
        :param vmrun_path: Path to the ``vmrun`` executable, or ``None`` to
            use the bare name ``"vmrun"`` and rely on ``$PATH``.
        :param host_type: Workstation host type passed as ``vmrun -T``;
            one of ``ws`` / ``fusion`` / ``player`` / ``server``.
        :param dry_run: When True, write operations short-circuit and
            return a ``DRY_RUN`` result without invoking the runner.
            Read operations (``list_running``, ``snapshot_list``,
            ``tools_state``) still execute.
    """

    def __init__(
        self,
        *,
        runner: ICommandRunner,
        vmrun_path: Optional[str] = None,
        host_type: str = _DEFAULT_HOST_TYPE,
        dry_run: bool = False,
    ) -> None:
        if host_type not in _SUPPORTED_HOST_TYPES:
            err_msg_lines = ["Unsupported VMware Workstation host_type."]
            err_msg_lines.append("    PROVIDED: {!r}".format(host_type))
            err_msg_lines.append(
                "    SUPPORTED: {}".format(list(_SUPPORTED_HOST_TYPES)),
            )
            err_msg = os.linesep.join(err_msg_lines)
            raise ValueError(err_msg)

        if vmrun_path is None or len(vmrun_path) == 0:
            resolved_vmrun_path = _DEFAULT_VMRUN_PATH
        else:
            resolved_vmrun_path = vmrun_path

        self._runner: ICommandRunner = runner
        self._vmrun_path: str = resolved_vmrun_path
        self._host_type: str = host_type
        self._dry_run: bool = dry_run
        self._dispatcher: VMRunDispatcher = VMRunDispatcher(
            runner=runner,
            vmrun_path=resolved_vmrun_path,
            host_type=host_type,
        )
        return

    @property
    def runner(self) -> ICommandRunner:
        """
            The injected command runner.
        """
        rtnval = self._runner
        return rtnval

    @property
    def vmrun_path(self) -> str:
        """
            The resolved ``vmrun`` executable path.
        """
        rtnval = self._vmrun_path
        return rtnval

    @property
    def host_type(self) -> str:
        """
            The configured ``-T`` host type.
        """
        rtnval = self._host_type
        return rtnval

    @property
    def dry_run(self) -> bool:
        """
            Whether the client is in dry-run mode.
        """
        rtnval = self._dry_run
        return rtnval

    # ------------------------------------------------------------------
    # VM lifecycle
    # ------------------------------------------------------------------

    def start(
        self,
        *,
        vmx_path: str,
        gui: bool = False,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Start a powered-off VM.

            :param vmx_path: Path to the ``.vmx`` file.
            :param gui: When True, start the VM with a UI window; otherwise
                start headless (``nogui``).
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        if gui is True:
            ui_mode = "gui"
        else:
            ui_mode = "nogui"

        subcommand_args = ["start", vmx_path, ui_mode]
        detail = "start {}".format(vmx_path)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def stop(
        self,
        *,
        vmx_path: str,
        hard: bool = False,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Stop a running VM.

            :param vmx_path: Path to the ``.vmx`` file.
            :param hard: When True, perform a hard power-off; otherwise
                request a soft shutdown via VMware Tools.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        if hard is True:
            stop_mode = "hard"
        else:
            stop_mode = "soft"

        subcommand_args = ["stop", vmx_path, stop_mode]
        detail = "stop {}".format(vmx_path)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def suspend(
        self,
        *,
        vmx_path: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Suspend a running VM.

            :param vmx_path: Path to the ``.vmx`` file.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args = ["suspend", vmx_path]
        detail = "suspend {}".format(vmx_path)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def reset(
        self,
        *,
        vmx_path: str,
        hard: bool = False,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Reset a running VM.

            :param vmx_path: Path to the ``.vmx`` file.
            :param hard: When True, perform a hard reset; otherwise request
                a soft reset via VMware Tools.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        if hard is True:
            reset_mode = "hard"
        else:
            reset_mode = "soft"

        subcommand_args = ["reset", vmx_path, reset_mode]
        detail = "reset {}".format(vmx_path)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    # ------------------------------------------------------------------
    # Snapshot lifecycle
    # ------------------------------------------------------------------

    def snapshot_create(
        self,
        *,
        vmx_path: str,
        name: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Create a snapshot.

            :param vmx_path: Path to the ``.vmx`` file.
            :param name: Snapshot name.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args = ["snapshot", vmx_path, name]
        detail = "snapshot_create {} {}".format(vmx_path, name)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def snapshot_revert(
        self,
        *,
        vmx_path: str,
        name: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Revert the VM to a named snapshot.

            :param vmx_path: Path to the ``.vmx`` file.
            :param name: Snapshot name.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args = ["revertToSnapshot", vmx_path, name]
        detail = "snapshot_revert {} {}".format(vmx_path, name)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def snapshot_delete(
        self,
        *,
        vmx_path: str,
        name: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Delete a named snapshot.

            :param vmx_path: Path to the ``.vmx`` file.
            :param name: Snapshot name.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args = ["deleteSnapshot", vmx_path, name]
        detail = "snapshot_delete {} {}".format(vmx_path, name)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def snapshot_list(
        self,
        *,
        vmx_path: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> List[SnapshotRecord]:
        """
            List snapshots for a VM.

            This is a read operation; it executes even in dry-run mode.

            :param vmx_path: Path to the ``.vmx`` file.
            :param aspects: Behaviour controls.

            :returns: A list of :class:`SnapshotRecord`.
            :raises VMRunCommandError: When ``vmrun`` exits non-zero.
            :raises VMWorkstationParseError: When the output cannot be
                parsed.
        """
        subcommand_args = ["listSnapshots", vmx_path]
        detail = "snapshot_list {}".format(vmx_path)

        run_result = self._dispatch_read(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )

        rtnval = parse_list_snapshots(payload=run_result.stdout)
        return rtnval

    # ------------------------------------------------------------------
    # Guest exec
    # ------------------------------------------------------------------

    def run_program_in_guest(
        self,
        *,
        vmx_path: str,
        guest_credential: GuestCredential,
        program: str,
        args: Optional[List[str]] = None,
        no_wait: bool = False,
        active_window: bool = False,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> GuestExecResult:
        """
            Run a program inside the guest OS via VMware Tools.

            :param vmx_path: Path to the ``.vmx`` file.
            :param guest_credential: Guest OS credentials.
            :param program: Absolute path of the program inside the guest.
            :param args: Optional list of program arguments.
            :param no_wait: When True, pass ``-noWait`` to ``vmrun``.
            :param active_window: When True, pass ``-activeWindow``.
            :param aspects: Behaviour controls.

            :returns: The :class:`GuestExecResult`.
        """
        if args is None:
            program_args: List[str] = []
        else:
            program_args = list(args)

        subcommand_args: List[str] = [
            "-gu", guest_credential.username,
            "-gp", guest_credential.password,
            "runProgramInGuest", vmx_path,
        ]
        if no_wait is True:
            subcommand_args.append("-noWait")
        if active_window is True:
            subcommand_args.append("-activeWindow")
        subcommand_args.append(program)
        subcommand_args.extend(program_args)

        detail = "run_program_in_guest {} {}".format(vmx_path, program)

        action_result = self._dispatch_guest_exec(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )

        rtnval = GuestExecResult(
            status=action_result.status,
            exit_code=action_result.exit_code,
            stdout=action_result.stdout,
            stderr=action_result.stderr,
            command=action_result.command,
        )
        return rtnval

    def copy_file_to_guest(
        self,
        *,
        vmx_path: str,
        guest_credential: GuestCredential,
        source: str,
        target: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Copy a file from the host into the guest.

            :param vmx_path: Path to the ``.vmx`` file.
            :param guest_credential: Guest OS credentials.
            :param source: Host-side source path.
            :param target: Guest-side destination path.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args: List[str] = [
            "-gu", guest_credential.username,
            "-gp", guest_credential.password,
            "copyFileFromHostToGuest", vmx_path,
            source, target,
        ]
        detail = "copy_file_to_guest {} -> {}".format(source, target)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def copy_file_from_guest(
        self,
        *,
        vmx_path: str,
        guest_credential: GuestCredential,
        source: str,
        target: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Copy a file from the guest into the host.

            This is technically a host-side write, so it honours dry-run.

            :param vmx_path: Path to the ``.vmx`` file.
            :param guest_credential: Guest OS credentials.
            :param source: Guest-side source path.
            :param target: Host-side destination path.
            :param aspects: Behaviour controls.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        subcommand_args: List[str] = [
            "-gu", guest_credential.username,
            "-gp", guest_credential.password,
            "copyFileFromGuestToHost", vmx_path,
            source, target,
        ]
        detail = "copy_file_from_guest {} -> {}".format(source, target)

        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            return dry

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval

    def tools_state(
        self,
        *,
        vmx_path: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> ToolsState:
        """
            Return the VMware Tools state inside the guest.

            This is a read operation; it executes even in dry-run mode.

            :param vmx_path: Path to the ``.vmx`` file.
            :param aspects: Behaviour controls.

            :returns: The :class:`ToolsState`.
            :raises VMRunCommandError: When ``vmrun`` exits non-zero.
        """
        subcommand_args = ["checkToolsState", vmx_path]
        detail = "tools_state {}".format(vmx_path)

        run_result = self._dispatch_read(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )

        rtnval = _map_tools_state(payload=run_result.stdout)
        return rtnval

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def list_running(
        self,
        *,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> List[str]:
        """
            List the VMX paths of running VMs.

            This is a read operation; it executes even in dry-run mode.

            :param aspects: Behaviour controls.

            :returns: A list of VMX paths.
            :raises VMRunCommandError: When ``vmrun`` exits non-zero.
            :raises VMWorkstationParseError: When the output cannot be
                parsed.
        """
        subcommand_args = ["list"]
        detail = "list_running"

        run_result = self._dispatch_read(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )

        rtnval = parse_list_running(payload=run_result.stdout)
        return rtnval

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _short_circuit_dry_run(
        self,
        *,
        subcommand_args: List[str],
        detail: str,
    ) -> Optional[VMWorkstationActionResult]:
        """
            If dry-run mode is active, build the argv that would have been
            dispatched and return a ``DRY_RUN`` result. Otherwise return
            ``None`` so the caller proceeds with dispatch.

            :param subcommand_args: The trailing ``vmrun`` subcommand and
                its parameters.
            :param detail: Free-form description carried on the result.

            :returns: A ``DRY_RUN`` :class:`VMWorkstationActionResult`, or
                ``None`` to indicate the caller should proceed.
        """
        if self._dry_run is False:
            rtnval: Optional[VMWorkstationActionResult] = None
            return rtnval

        argv = self._dispatcher.build_argv(subcommand_args=subcommand_args)
        safe_argv = redact_argv(argv=argv)
        rtnval = VMWorkstationActionResult(
            status=VMWorkstationActionStatus.DRY_RUN,
            detail=detail,
            exit_code=None,
            stdout=None,
            stderr=None,
            command=safe_argv,
        )
        return rtnval

    def _dispatch_read(
        self,
        *,
        subcommand_args: List[str],
        detail: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> RunResult:
        """
            Dispatch a read-only ``vmrun`` invocation and return the raw
            :class:`RunResult`. Read paths never dry-run-short-circuit.

            :param subcommand_args: The trailing ``vmrun`` subcommand and
                its parameters.
            :param detail: Free-form description used in error messages.
            :param aspects: Behaviour controls. When ``None`` a fresh
                default :class:`AspectsVMWorkstation` is used.

            :returns: The raw :class:`RunResult`.
            :raises VMRunCommandError: When ``vmrun`` exits non-zero.
        """
        if aspects is None:
            resolved_aspects = AspectsVMWorkstation()
        else:
            resolved_aspects = aspects

        argv = self._dispatcher.build_argv(subcommand_args=subcommand_args)
        run_result: RunResult = self._runner.run(
            list(argv),
            elevated=resolved_aspects.elevated,
            timeout=resolved_aspects.command_timeout,
        )

        if run_result.exit_code != 0:
            safe_argv = redact_argv(argv=argv)
            err_msg_lines = ["vmrun read invocation failed."]
            err_msg_lines.append("    DETAIL: {}".format(detail))
            err_msg_lines.append(
                "    COMMAND: {}".format(" ".join(safe_argv)),
            )
            err_msg_lines.append(
                "    EXIT_CODE: {}".format(run_result.exit_code),
            )
            err_msg_lines.append("    STDERR: {}".format(run_result.stderr))
            err_msg = os.linesep.join(err_msg_lines)
            raise VMRunCommandError(
                message=err_msg,
                exit_code=run_result.exit_code,
                stdout=run_result.stdout,
                stderr=run_result.stderr,
                command=safe_argv,
            )

        rtnval = run_result
        return rtnval

    def _dispatch_guest_exec(
        self,
        *,
        subcommand_args: List[str],
        detail: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Dispatch a guest-exec ``vmrun`` invocation, honouring dry-run.

            :param subcommand_args: The trailing ``vmrun`` subcommand and
                its parameters.
            :param detail: Free-form description carried on the result.
            :param aspects: Behaviour controls. When ``None`` the dispatcher
                applies a fresh default :class:`AspectsVMWorkstation`.

            :returns: The :class:`VMWorkstationActionResult`.
        """
        dry = self._short_circuit_dry_run(
            subcommand_args=subcommand_args, detail=detail,
        )
        if dry is not None:
            rtnval = dry
            return rtnval

        rtnval = self._dispatcher.dispatch(
            subcommand_args=subcommand_args,
            detail=detail,
            aspects=aspects,
        )
        return rtnval


# ----------------------------------------------------------------------
# Module-level helpers
# ----------------------------------------------------------------------


def _map_tools_state(*, payload: str) -> ToolsState:
    """
        Map ``vmrun checkToolsState`` stdout to a :class:`ToolsState`.

        ``vmrun`` prints a single word (``installed`` / ``running`` /
        ``unknown``) or ``"not installed"``. Whitespace and case are
        normalised before matching.

        :param payload: The decoded stdout from ``vmrun``.

        :returns: The :class:`ToolsState`.
    """
    if payload is None:
        text = ""
    else:
        text = payload
    normalised = text.strip().lower()

    if normalised == "running":
        rtnval = ToolsState.RUNNING
        return rtnval
    if normalised == "installed":
        rtnval = ToolsState.INSTALLED
        return rtnval
    if normalised == "not installed":
        rtnval = ToolsState.NOT_INSTALLED
        return rtnval

    rtnval = ToolsState.UNKNOWN
    return rtnval


__all__ = ["VMWorkstationClient"]
