"""
    .. module:: aspectsvmworkstation
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Behaviour-modifying parameters for the VMware Workstation
                   interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Optional

from automojo.aspects.aspects import Aspects


@dataclass
class AspectsVMWorkstation(Aspects):
    """
        Workstation-specific behaviour carrier.

        Inherits the generic completion / timeout / attempt fields from
        :class:`Aspects` and adds the small set of behaviour controls the
        ``vmrun`` dispatcher honours.

        :param elevated: When True, the runner is invoked with ``elevated``.
        :param raise_on_failure: When True, non-zero ``vmrun`` exits raise a
            :class:`VMRunCommandError` instead of returning a ``FAILED``
            result.
        :param command_timeout: Per-invocation timeout passed through to the
            runner. ``None`` means no enforced timeout at the runner.
    """
    elevated: bool = False
    raise_on_failure: bool = False
    command_timeout: Optional[float] = None


DEFAULT_VMWORKSTATION_ASPECTS = AspectsVMWorkstation()


__all__ = [
    "AspectsVMWorkstation",
    "DEFAULT_VMWORKSTATION_ASPECTS",
]
