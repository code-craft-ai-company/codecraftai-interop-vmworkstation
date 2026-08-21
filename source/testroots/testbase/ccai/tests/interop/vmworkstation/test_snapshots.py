"""
    Tests for snapshot lifecycle on :class:`VMWorkstationClient`.
"""

import os


from ccai.interfaces.icommandrunner import RunResult

from ccai.interop.vmworkstation import (
    VMRunCommandError,
    VMWorkstationActionStatus,
    VMWorkstationClient,
    VMWorkstationParseError,
)
from ccai.interop.vmworkstation.snapshots import (
    parse_list_snapshots,
    parse_list_running,
)

from .mockcommandrunner import (
    MockCommandRunner,
)

from ccai import testbase


_VMX = "/vms/u.vmx"


def _ok(stdout: str = "") -> RunResult:
    return RunResult(exit_code=0, stdout=stdout, stderr="")


def _fail() -> RunResult:
    return RunResult(exit_code=1, stdout="", stderr="boom")


def test_snapshot_create_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "snapshot", _VMX, "baseline"],
        result=_ok(),
    )
    client = VMWorkstationClient(runner=runner)

    result = client.snapshot_create(vmx_path=_VMX, name="baseline")

    assert result.status == VMWorkstationActionStatus.SUCCESS


def test_snapshot_revert_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=[
            "vmrun", "-T", "ws", "revertToSnapshot", _VMX, "baseline",
        ],
        result=_ok(),
    )
    client = VMWorkstationClient(runner=runner)

    result = client.snapshot_revert(vmx_path=_VMX, name="baseline")

    assert result.status == VMWorkstationActionStatus.SUCCESS


def test_snapshot_delete_argv() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=[
            "vmrun", "-T", "ws", "deleteSnapshot", _VMX, "baseline",
        ],
        result=_ok(),
    )
    client = VMWorkstationClient(runner=runner)

    result = client.snapshot_delete(vmx_path=_VMX, name="baseline")

    assert result.status == VMWorkstationActionStatus.SUCCESS


def test_snapshot_list_empty() -> None:
    payload = "Total snapshots: 0" + os.linesep
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "listSnapshots", _VMX],
        result=_ok(stdout=payload),
    )
    client = VMWorkstationClient(runner=runner)

    records = client.snapshot_list(vmx_path=_VMX)

    assert records == []


def test_snapshot_list_multiple() -> None:
    payload_lines = [
        "Total snapshots: 3",
        "baseline",
        "post-install",
        "pre-upgrade",
    ]
    payload = os.linesep.join(payload_lines) + os.linesep
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "listSnapshots", _VMX],
        result=_ok(stdout=payload),
    )
    client = VMWorkstationClient(runner=runner)

    records = client.snapshot_list(vmx_path=_VMX)

    assert len(records) == 3
    names = [rec.name for rec in records]
    assert names == ["baseline", "post-install", "pre-upgrade"]


def test_snapshot_list_failed_raises() -> None:
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "listSnapshots", _VMX],
        result=_fail(),
    )
    client = VMWorkstationClient(runner=runner)

    with testbase.raises(VMRunCommandError):
        client.snapshot_list(vmx_path=_VMX)


def test_snapshot_list_parse_bad_header() -> None:
    with testbase.raises(VMWorkstationParseError):
        parse_list_snapshots(payload="garbage line" + os.linesep + "x")


def test_snapshot_list_parse_count_mismatch() -> None:
    payload = os.linesep.join(["Total snapshots: 2", "only_one"])
    with testbase.raises(VMWorkstationParseError):
        parse_list_snapshots(payload=payload)


def test_parse_list_running_zero() -> None:
    payload = "Total running VMs: 0" + os.linesep
    paths = parse_list_running(payload=payload)
    assert paths == []


def test_parse_list_running_one() -> None:
    payload = os.linesep.join(["Total running VMs: 1", "/vms/a.vmx"])
    paths = parse_list_running(payload=payload)
    assert paths == ["/vms/a.vmx"]


def test_parse_list_running_many() -> None:
    payload = os.linesep.join([
        "Total running VMs: 3",
        "/vms/a.vmx",
        "/vms/b.vmx",
        "/vms/c.vmx",
    ])
    paths = parse_list_running(payload=payload)
    assert paths == ["/vms/a.vmx", "/vms/b.vmx", "/vms/c.vmx"]


def test_parse_list_running_bad_header() -> None:
    with testbase.raises(VMWorkstationParseError):
        parse_list_running(payload="something else\n/vms/a.vmx")


def test_snapshot_dry_run() -> None:
    runner = MockCommandRunner()
    client = VMWorkstationClient(runner=runner, dry_run=True)

    result = client.snapshot_create(vmx_path=_VMX, name="x")

    assert result.status == VMWorkstationActionStatus.DRY_RUN
    assert len(runner.calls) == 0


def test_snapshot_list_executes_under_dry_run() -> None:
    payload = "Total snapshots: 0" + os.linesep
    runner = MockCommandRunner()
    runner.seed(
        argv=["vmrun", "-T", "ws", "listSnapshots", _VMX],
        result=_ok(stdout=payload),
    )
    client = VMWorkstationClient(runner=runner, dry_run=True)

    records = client.snapshot_list(vmx_path=_VMX)

    assert records == []
    assert len(runner.calls) == 1
