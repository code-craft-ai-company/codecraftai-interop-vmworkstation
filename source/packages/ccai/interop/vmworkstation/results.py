"""
    .. module:: results
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Result types for the VMware Workstation interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class VMWorkstationActionStatus(Enum):
    """
        Status enumeration for ``vmrun`` action results.
    """
    SUCCESS = "success"
    FAILED = "failed"
    DRY_RUN = "dry_run"


class ToolsState(Enum):
    """
        VMware Tools state as reported by ``vmrun checkToolsState``.
    """
    INSTALLED = "installed"
    RUNNING = "running"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"


@dataclass
class VMWorkstationActionResult:
    """
        Result of a ``vmrun`` action invocation.

        :param status: The outcome status.
        :param detail: Free-form description of the action context.
        :param exit_code: The ``vmrun`` exit code, when available.
        :param stdout: Captured stdout, when available.
        :param stderr: Captured stderr, when available.
        :param command: The argv that was dispatched, when available.
    """
    status: VMWorkstationActionStatus
    detail: Optional[str]
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    command: Optional[List[str]]


@dataclass
class GuestExecResult:
    """
        Result of a guest-exec ``vmrun`` invocation.

        :param status: The outcome status.
        :param exit_code: The ``vmrun`` exit code, when available.
        :param stdout: Captured stdout, when available.
        :param stderr: Captured stderr, when available.
        :param command: The argv that was dispatched, when available.
    """
    status: VMWorkstationActionStatus
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    command: Optional[List[str]]


__all__ = [
    "GuestExecResult",
    "ToolsState",
    "VMWorkstationActionResult",
    "VMWorkstationActionStatus",
]
