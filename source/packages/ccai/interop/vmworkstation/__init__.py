"""
    .. module:: vmworkstation
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Public exports for the VMware Workstation interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vmworkstation.aspectsvmworkstation import (
    AspectsVMWorkstation,
    DEFAULT_VMWORKSTATION_ASPECTS,
)
from ccai.interop.vmworkstation.exceptions import (
    VMWorkstationError,
    VMRunCommandError,
    VMWorkstationParseError,
)
from ccai.interop.vmworkstation.guestcredential import GuestCredential
from ccai.interop.vmworkstation.redaction import redact_argv
from ccai.interop.vmworkstation.results import (
    GuestExecResult,
    ToolsState,
    VMWorkstationActionResult,
    VMWorkstationActionStatus,
)
from ccai.interop.vmworkstation.snapshots import SnapshotRecord
from ccai.interop.vmworkstation.vmworkstationclient import VMWorkstationClient


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
