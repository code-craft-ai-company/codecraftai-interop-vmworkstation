"""
    .. module:: vmworkstation
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Public exports for the VMware Workstation interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vmworkstation.aspectsvmworkstation import (
    AspectsVMWorkstation,
    DEFAULT_VMWORKSTATION_ASPECTS,
)
from automojo.interop.vmworkstation.exceptions import (
    VMWorkstationError,
    VMRunCommandError,
    VMWorkstationParseError,
)
from automojo.interop.vmworkstation.guestcredential import GuestCredential
from automojo.interop.vmworkstation.redaction import redact_argv
from automojo.interop.vmworkstation.results import (
    GuestExecResult,
    ToolsState,
    VMWorkstationActionResult,
    VMWorkstationActionStatus,
)
from automojo.interop.vmworkstation.snapshots import SnapshotRecord
from automojo.interop.vmworkstation.vmworkstationclient import VMWorkstationClient


__all__ = [
    "AspectsVMWorkstation",
    "DEFAULT_VMWORKSTATION_ASPECTS",
    "GuestCredential",
    "GuestExecResult",
    "redact_argv",
    "SnapshotRecord",
    "ToolsState",
    "VMRunCommandError",
    "VMWorkstationActionResult",
    "VMWorkstationActionStatus",
    "VMWorkstationClient",
    "VMWorkstationError",
    "VMWorkstationParseError",
]
