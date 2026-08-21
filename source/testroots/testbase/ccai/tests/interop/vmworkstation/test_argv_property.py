"""
    Property tests asserting deterministic argv construction.
"""

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.interfaces.icommandrunner import RunResult

from ccai.interop.vmworkstation import VMWorkstationClient

from .mockcommandrunner import (
    MockCommandRunner,
)


_HOST_TYPES = st.sampled_from(["ws", "fusion", "player", "server"])
_VMX_PATHS = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        whitelist_characters="/.-_",
    ),
    min_size=1,
    max_size=64,
).map(lambda v: "/vms/" + v + ".vmx")
_SNAPSHOT_NAMES = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        whitelist_characters="-_.",
    ),
    min_size=1,
    max_size=32,
)


def _ok() -> RunResult:
    return RunResult(exit_code=0, stdout="", stderr="")


@given(host=_HOST_TYPES, vmx=_VMX_PATHS, gui=st.booleans())
def test_start_argv_is_deterministic(*, host: str, vmx: str, gui: bool) -> None:
    if gui is True:
        mode = "gui"
    else:
        mode = "nogui"
    expected = ["vmrun", "-T", host, "start", vmx, mode]

    first_runner = MockCommandRunner(default=_ok())
    first_client = VMWorkstationClient(runner=first_runner, host_type=host)
    first_result = first_client.start(vmx_path=vmx, gui=gui)

    second_runner = MockCommandRunner(default=_ok())
    second_client = VMWorkstationClient(runner=second_runner, host_type=host)
    second_result = second_client.start(vmx_path=vmx, gui=gui)

    assert first_result.command == expected
    assert second_result.command == expected
    assert first_runner.calls[0][0] == second_runner.calls[0][0]


@given(host=_HOST_TYPES, vmx=_VMX_PATHS, name=_SNAPSHOT_NAMES)
def test_snapshot_create_argv_is_deterministic(
    *, host: str, vmx: str, name: str,
) -> None:
    expected = ["vmrun", "-T", host, "snapshot", vmx, name]

    first_runner = MockCommandRunner(default=_ok())
    first_client = VMWorkstationClient(runner=first_runner, host_type=host)
    first_result = first_client.snapshot_create(vmx_path=vmx, name=name)

    second_runner = MockCommandRunner(default=_ok())
    second_client = VMWorkstationClient(runner=second_runner, host_type=host)
    second_result = second_client.snapshot_create(vmx_path=vmx, name=name)

    assert first_result.command == expected
    assert second_result.command == expected


@given(host=_HOST_TYPES, vmx=_VMX_PATHS, hard=st.booleans())
def test_stop_argv_is_deterministic(
    *, host: str, vmx: str, hard: bool,
) -> None:
    if hard is True:
        mode = "hard"
    else:
        mode = "soft"
    expected = ["vmrun", "-T", host, "stop", vmx, mode]

    runner_a = MockCommandRunner(default=_ok())
    client_a = VMWorkstationClient(runner=runner_a, host_type=host)
    result_a = client_a.stop(vmx_path=vmx, hard=hard)

    runner_b = MockCommandRunner(default=_ok())
    client_b = VMWorkstationClient(runner=runner_b, host_type=host)
    result_b = client_b.stop(vmx_path=vmx, hard=hard)

    assert result_a.command == expected
    assert result_b.command == expected
