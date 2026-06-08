"""
    Regression tests for NR-H1: the guest password passed via ``-gp`` must
    never appear in plaintext on result objects, exceptions, or error
    messages returned to callers.
"""

import pytest

from ccai.interfaces.icommandrunner import RunResult

from ccai.interop.vmworkstation import (
    AspectsVMWorkstation,
    GuestCredential,
    VMRunCommandError,
    VMWorkstationActionStatus,
    VMWorkstationClient,
    redact_argv,
)

from ccai.tests.interop.vmworkstation.mockcommandrunner import (
    MockCommandRunner,
)


_VMX = "/vms/u.vmx"
_SECRET = "sup3r-s3cr3t-pw"


def _cred() -> GuestCredential:
    return GuestCredential(username="u", password=_SECRET)


def _ok() -> RunResult:
    return RunResult(exit_code=0, stdout="", stderr="")


def _fail() -> RunResult:
    return RunResult(exit_code=2, stdout="", stderr="guest-error")


def test_redact_argv_scrubs_gp_value() -> None:
    argv = ["vmrun", "-gu", "u", "-gp", _SECRET, "runProgramInGuest"]
    result = redact_argv(argv=argv)
    assert _SECRET not in result
    assert result[4] == "<redacted>"


def test_redact_argv_none_passthrough() -> None:
    result = redact_argv(argv=None)
    assert result is None


def test_redact_argv_does_not_mutate_input() -> None:
    argv = ["vmrun", "-gp", _SECRET]
    redact_argv(argv=argv)
    assert argv[2] == _SECRET


def test_run_program_result_command_redacted() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", _SECRET,
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
    assert _SECRET not in result.command


def test_run_program_dry_run_command_redacted() -> None:
    runner = MockCommandRunner()
    client = VMWorkstationClient(runner=runner, dry_run=True)

    result = client.run_program_in_guest(
        vmx_path=_VMX,
        guest_credential=_cred(),
        program="/bin/true",
    )

    assert result.status == VMWorkstationActionStatus.DRY_RUN
    assert _SECRET not in result.command


def test_run_program_failure_exception_redacted() -> None:
    dispatched = [
        "vmrun", "-T", "ws",
        "-gu", "u", "-gp", _SECRET,
        "runProgramInGuest", _VMX,
        "/bin/false",
    ]
    runner = MockCommandRunner()
    runner.seed(argv=dispatched, result=_fail())
    client = VMWorkstationClient(runner=runner)

    with pytest.raises(VMRunCommandError) as excinfo:
        client.run_program_in_guest(
            vmx_path=_VMX,
            guest_credential=_cred(),
            program="/bin/false",
            aspects=AspectsVMWorkstation(raise_on_failure=True),
        )

    error = excinfo.value
    assert _SECRET not in error.message
    assert _SECRET not in str(error)
    assert _SECRET not in error.command
