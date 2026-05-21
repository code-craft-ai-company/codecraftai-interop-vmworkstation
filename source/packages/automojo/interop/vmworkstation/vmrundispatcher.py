"""
    .. module:: vmrundispatcher
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: ``vmrun`` argv construction and dispatch through an
                   :class:`ICommandRunner`.

    The dispatcher centralises argv prefix construction
    (``<vmrun_path> -T <host_type> ...``), runner invocation, and the
    success/failure result mapping. It does NOT make policy decisions about
    dry-run; that responsibility lives in :class:`VMWorkstationClient`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import List, Optional

from automojo.interfaces.icommandrunner import ICommandRunner, RunResult

from automojo.interop.vmworkstation.aspectsvmworkstation import (
    AspectsVMWorkstation,
)
from automojo.interop.vmworkstation.exceptions import VMRunCommandError
from automojo.interop.vmworkstation.redaction import redact_argv
from automojo.interop.vmworkstation.results import (
    VMWorkstationActionResult,
    VMWorkstationActionStatus,
)


class VMRunDispatcher:
    """
        Builds ``vmrun`` argv and dispatches it through an
        :class:`ICommandRunner`.

        The dispatcher is deliberately small: argv prefix + invocation +
        result mapping. Output parsing belongs in the caller (the client).

        :param runner: The injected command runner.
        :param vmrun_path: Absolute path to the ``vmrun`` executable, or the
            bare name ``"vmrun"`` to rely on ``$PATH`` resolution by the
            runner.
        :param host_type: The ``-T`` value passed to every invocation
            (``ws`` / ``fusion`` / ``player`` / ``server``).
    """

    def __init__(
        self,
        *,
        runner: ICommandRunner,
        vmrun_path: str,
        host_type: str,
    ) -> None:
        self._runner: ICommandRunner = runner
        self._vmrun_path: str = vmrun_path
        self._host_type: str = host_type
        return

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

    def build_argv(self, *, subcommand_args: List[str]) -> List[str]:
        """
            Build the full argv for a ``vmrun`` invocation.

            :param subcommand_args: The trailing ``vmrun`` subcommand and
                its parameters, e.g. ``["start", vmx, "nogui"]``.

            :returns: The full argv beginning with the ``vmrun`` executable.
        """
        argv: List[str] = [self._vmrun_path, "-T", self._host_type]
        argv.extend(subcommand_args)
        rtnval = argv
        return rtnval

    def dispatch(
        self,
        *,
        subcommand_args: List[str],
        detail: str,
        aspects: Optional[AspectsVMWorkstation] = None,
    ) -> VMWorkstationActionResult:
        """
            Build argv, run it through the runner, and map the
            :class:`RunResult` to a :class:`VMWorkstationActionResult`.

            :param subcommand_args: The trailing ``vmrun`` subcommand and
                its parameters.
            :param detail: Free-form description carried on the result for
                debuggability.
            :param aspects: Behaviour controls
                (elevation, raise-on-failure, timeout). When ``None`` a
                fresh default :class:`AspectsVMWorkstation` is used.

            :returns: The :class:`VMWorkstationActionResult`.
            :raises VMRunCommandError: When the invocation exits non-zero
                and ``aspects.raise_on_failure`` is True.
        """
        if aspects is None:
            resolved_aspects = AspectsVMWorkstation()
        else:
            resolved_aspects = aspects

        argv = self.build_argv(subcommand_args=subcommand_args)

        run_result: RunResult = self._runner.run(
            list(argv),
            elevated=resolved_aspects.elevated,
            timeout=resolved_aspects.command_timeout,
        )

        safe_argv = redact_argv(argv=argv)

        exit_code = run_result.exit_code
        if exit_code == 0:
            mapped_status = VMWorkstationActionStatus.SUCCESS
        else:
            mapped_status = VMWorkstationActionStatus.FAILED

        rtnval = VMWorkstationActionResult(
            status=mapped_status,
            detail=detail,
            exit_code=exit_code,
            stdout=run_result.stdout,
            stderr=run_result.stderr,
            command=safe_argv,
        )

        if mapped_status == VMWorkstationActionStatus.FAILED:
            if resolved_aspects.raise_on_failure is True:
                err_msg_lines = ["vmrun invocation failed."]
                err_msg_lines.append("    DETAIL: {}".format(detail))
                err_msg_lines.append(
                    "    COMMAND: {}".format(" ".join(safe_argv)),
                )
                err_msg_lines.append("    EXIT_CODE: {}".format(exit_code))
                err_msg_lines.append(
                    "    STDERR: {}".format(run_result.stderr),
                )
                err_msg = os.linesep.join(err_msg_lines)
                raise VMRunCommandError(
                    message=err_msg,
                    exit_code=exit_code,
                    stdout=run_result.stdout,
                    stderr=run_result.stderr,
                    command=safe_argv,
                )

        return rtnval


__all__ = ["VMRunDispatcher"]
