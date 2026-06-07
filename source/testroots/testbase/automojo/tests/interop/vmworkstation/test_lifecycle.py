"""
    Tests for VM lifecycle methods on :class:`VMWorkstationClient`.
"""

import pytest

from ccai.interfaces.icommandrunner import RunResult

from ccai.interop.vmworkstation import (
    DEFAULT_VMWORKSTATION_ASPECTS,
    VMRunCommandError,
    VMWorkstationActionStatus,
    VMWorkstationClient,
)
from ccai.interop.vmworkstation.aspectsvmworkstation import (
    AspectsVMWorkstation,
)

from ccai.tests.interop.vmworkstation.mockcommandrunner import (
    MockCommandRunner,
)


_VMX = "/var/lib/vmware/vms/u22.vmx"


def _ok() -> RunResult:
    return RunResult(exit_code=0, stdout="", stderr="")


def _fail() -> RunResult:
    return RunResult(exit_code=4, stdout="", stderr="vmrun: bad path")


def _build_client(runner: MockCommandRunner) -> VMWorkstationClient:
    client = VMWorkstationClient(runner=runner)
    return client


def test_start_nogui_happy_path() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "start", _VMX, "nogui"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.start(vmx_path=_VMX)

    assert result.status == VMWorkstationActionStatus.SUCCESS
    assert result.command == ["vmrun", "-T", "ws", "start", _VMX, "nogui"]
    assert result.exit_code == 0
    assert len(runner.calls) == 1


def test_start_gui_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "start", _VMX, "gui"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.start(vmx_path=_VMX, gui=True)

    assert result.status == VMWorkstationActionStatus.SUCCESS
    assert "gui" in result.command


def test_stop_soft_default() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "stop", _VMX, "soft"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.stop(vmx_path=_VMX)

    assert result.status == VMWorkstationActionStatus.SUCCESS
    assert result.command[-1] == "soft"


def test_stop_hard_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "stop", _VMX, "hard"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.stop(vmx_path=_VMX, hard=True)

    assert result.command[-1] == "hard"


def test_suspend_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "suspend", _VMX],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.suspend(vmx_path=_VMX)

    assert result.status == VMWorkstationActionStatus.SUCCESS


def test_reset_soft_default() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "reset", _VMX, "soft"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.reset(vmx_path=_VMX)

    assert result.command[-1] == "soft"


def test_reset_hard_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "reset", _VMX, "hard"],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    result = client.reset(vmx_path=_VMX, hard=True)

    assert result.command[-1] == "hard"


def test_lifecycle_failure_returns_failed_with_stderr() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "start", _VMX, "nogui"],
        result=_fail(),
    )
    client = _build_client(runner=runner)

    result = client.start(vmx_path=_VMX)

    assert result.status == VMWorkstationActionStatus.FAILED
    assert result.exit_code == 4
    assert result.stderr == "vmrun: bad path"


def test_lifecycle_failure_raises_when_aspect_set() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "start", _VMX, "nogui"],
        result=_fail(),
    )
    client = _build_client(runner=runner)
    aspects = AspectsVMWorkstation(raise_on_failure=True)

    with pytest.raises(VMRunCommandError) as exc_info:
        client.start(vmx_path=_VMX, aspects=aspects)

    assert exc_info.value.exit_code == 4
    assert exc_info.value.stderr == "vmrun: bad path"


def test_dry_run_short_circuits_runner() -> None:
    runner = MockCommandRunner()
    client = VMWorkstationClient(runner=runner, dry_run=True)

    result = client.start(vmx_path=_VMX)

    assert result.status == VMWorkstationActionStatus.DRY_RUN
    assert result.command == ["vmrun", "-T", "ws", "start", _VMX, "nogui"]
    assert len(runner.calls) == 0


def test_default_aspects_propagate_timeout_none() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "suspend", _VMX],
        result=_ok(),
    )
    client = _build_client(runner=runner)

    client.suspend(vmx_path=_VMX, aspects=DEFAULT_VMWORKSTATION_ASPECTS)

    args, kwargs = runner.calls[0]
    assert kwargs["timeout"] is None
    assert kwargs["elevated"] is False


def test_host_type_fusion() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "fusion", "suspend", _VMX],
        result=_ok(),
    )
    client = VMWorkstationClient(runner=runner, host_type="fusion")

    result = client.suspend(vmx_path=_VMX)

    assert result.command[2] == "fusion"


def test_invalid_host_type_raises() -> None:
    runner = MockCommandRunner()
    with pytest.raises(ValueError):
        VMWorkstationClient(runner=runner, host_type="bogus")


def test_vmrun_path_override() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["/opt/vmware/vmrun", "-T", "ws", "suspend", _VMX],
        result=_ok(),
    )
    client = VMWorkstationClient(
        runner=runner, vmrun_path="/opt/vmware/vmrun",
    )

    result = client.suspend(vmx_path=_VMX)

    assert result.command[0] == "/opt/vmware/vmrun"
