"""
    .. module:: exceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Typed exceptions raised by the VMware Workstation interop
                   client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Optional


class VMWorkstationError(Exception):
    """
        Base class for all VMware Workstation interop errors.
    """


class VMRunCommandError(VMWorkstationError):
    """
        Raised when a ``vmrun`` invocation exits non-zero and the caller has
        opted into exception-on-failure behaviour.

        :param message: Human-readable failure description.
        :param exit_code: The ``vmrun`` exit code, when available.
        :param stdout: Captured stdout, when available.
        :param stderr: Captured stderr, when available.
        :param command: The argv that was dispatched, when available.
    """

    def __init__(
        self,
        *,
        message: str,
        exit_code: Optional[int],
        stdout: Optional[str],
        stderr: Optional[str],
        command: Optional[list],
    ) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        return


class VMWorkstationParseError(VMWorkstationError):
    """
        Raised when ``vmrun`` output cannot be parsed into the expected
        structure.

        :param message: Human-readable description of the parse failure.
        :param raw_output: The raw output that could not be parsed.
    """

    def __init__(
        self,
        *,
        message: str,
        raw_output: Optional[str],
    ) -> None:
        super().__init__(message)
        self.message = message
        self.raw_output = raw_output
        return


__all__ = [
    "VMRunCommandError",
    "VMWorkstationError",
    "VMWorkstationParseError",
]
