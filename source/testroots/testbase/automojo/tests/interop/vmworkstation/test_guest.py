"""
    Tests for guest-exec and tools_state methods on
    :class:`VMWorkstationClient`.
"""

import os

import pytest

from ccai.interfaces.icommandrunner import RunResult

from ccai.interop.vmworkstation import (
    GuestCredential,
    ToolsState,
    VMRunCommandError,
    VMWorkstationActionStatus,
    VMWorkstationClient,
)

from ccai.tests.interop.vmworkstation.mockcommandrunner import (
    MockCommandRunner,
)


_VMX = "/vms/u.vmx"


def _cred() -> GuestCredential:
    return GuestCredential(username="u", password="p")


def _ok(stdout: str = "") -> RunResult:
    return RunResult(exit_code=0, stdout=stdout, stderr="")


def _fail() -> RunResult:
    return RunResult(exit_code=2, stdout="", stderr="guest-error")


def test_run_program_in_guest_minimal_argv() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "p",
        "runProgramInGuest", _VMX,
        "/bin/true",
    ]
    redacted = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "<redacted>",
        "runProgramInGuest", _VMX,
        "/bin/true",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=dispatched, result=_ok())
    client = VMWorkstationClient(runner=runner)

    result = client.run_program_in_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        program="/bin/true",
    )

    assert result.status == VMWorkstationActionStatus.SUCCESS
    assert result.command == redacted


def test_run_program_in_guest_full_argv() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "p",
        "runProgramInGuest", _VMX,
        "-noWait", "-activeWindow",
        "/bin/echo", "hello", "world",
    ]
    redacted = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "<redacted>",
        "runProgramInGuest", _VMX,
        "-noWait", "-activeWindow",
        "/bin/echo", "hello", "world",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=dispatched, result=_ok())
    client = VMWorkstationClient(runner=runner)

    result = client.run_program_in_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        program="/bin/echo",
        args=["hello", "world"],
        no_wait=True,
        active_window=True,
    )

    assert result.command == redacted


def test_run_program_in_guest_failure() -> None:
    expected = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "p",
        "runProgramInGuest", _VMX,
        "/bin/false",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=expected, result=_fail())
    client = VMWorkstationClient(runner=runner)

    result = client.run_program_in_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        program="/bin/false",
    )

    assert result.status == VMWorkstationActionStatus.FAILED
    assert result.stderr == "guest-error"


def test_copy_file_to_guest_argv() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "p",
        "copyFileFromHostToGuest", _VMX,
        "/host/a", "/guest/a",
    ]
    redacted = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "<redacted>",
        "copyFileFromHostToGuest", _VMX,
        "/host/a", "/guest/a",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=dispatched, result=_ok())
    client = VMWorkstationClient(runner=runner)

    result = client.copy_file_to_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        source="/host/a",
        target="/guest/a",
    )

    assert result.command == redacted


def test_copy_file_from_guest_argv() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "p",
        "copyFileFromGuestToHost", _VMX,
        "/guest/a", "/host/a",
    ]
    redacted = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", "<redacted>",
        "copyFileFromGuestToHost", _VMX,
        "/guest/a", "/host/a",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=dispatched, result=_ok())
    client = VMWorkstationClient(runner=runner)

    result = client.copy_file_from_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        source="/guest/a",
        target="/host/a",
    )

    assert result.command == redacted


def test_run_program_in_guest_dry_run() -> None:
    runner = MockCommandRunner()
    client = VMWorkstationClient(runner=runner, dry_run=True)

    result = client.run_program_in_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        program="/bin/true",
    )

    assert result.status == VMWorkstationActionStatus.DRY_RUN
    assert len(runner.calls) == 0


def test_tools_state_running() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "checkToolsState", _VMX],
        result=_ok(stdout="running" + os.linesep),
    )
    client = VMWorkstationClient(runner=runner)

    state = client.tools_state(vmx_path=_VMX)

    assert state == ToolsState.RUNNING


def test_tools_state_installed() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "checkToolsState", _VMX],
        result=_ok(stdout="installed\n"),
    )
    client = VMWorkstationClient(runner=runner)

    state = client.tools_state(vmx_path=_VMX)

    assert state == ToolsState.INSTALLED


def test_tools_state_not_installed() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "checkToolsState", _VMX],
        result=_ok(stdout="not installed\n"),
    )
    client = VMWorkstationClient(runner=runner)

    state = client.tools_state(vmx_path=_VMX)

    assert state == ToolsState.NOT_INSTALLED


def test_tools_state_unknown() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "checkToolsState", _VMX],
        result=_ok(stdout="something weird\n"),
    )
    client = VMWorkstationClient(runner=runner)

    state = client.tools_state(vmx_path=_VMX)

    assert state == ToolsState.UNKNOWN


def test_tools_state_failure_raises() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "checkToolsState", _VMX],
        result=_fail(),
    )
    client = VMWorkstationClient(runner=runner)

    with pytest.raises(VMRunCommandError):
        client.tools_state(vmx_path=_VMX)


def test_list_running_happy_path() -> None:
    payload = os.linesep.join([
        "Total running VMs: 2",
        "/vms/a.vmx",
        "/vms/b.vmx",
    ])
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "list"],
        result=_ok(stdout=payload),
    )
    client = VMWorkstationClient(runner=runner)

    paths = client.list_running()

    assert paths == ["/vms/a.vmx", "/vms/b.vmx"]


def test_list_running_failure_raises() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "list"],
        result=_fail(),
    )
    client = VMWorkstationClient(runner=runner)

    with pytest.raises(VMRunCommandError):
        client.list_running()
