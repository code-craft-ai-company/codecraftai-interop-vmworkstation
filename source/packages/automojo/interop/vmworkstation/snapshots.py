"""
    .. module:: snapshots
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: ``vmrun listSnapshots`` parsing and the
                   :class:`SnapshotRecord` data class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from dataclasses import dataclass
from typing import List, Optional

from automojo.interop.vmworkstation.exceptions import VMWorkstationParseError


@dataclass
class SnapshotRecord:
    """
        Record describing one snapshot reported by ``vmrun listSnapshots``.

        :param name: The snapshot name (as printed by ``vmrun``).
        :param parent: The parent snapshot name, or ``None`` for top-level.
    """
    name: str
    parent: Optional[str]


def parse_list_snapshots(*, payload: str) -> List[SnapshotRecord]:
    """
        Parse the stdout of ``vmrun listSnapshots <vmx>``.

        ``vmrun listSnapshots`` typically prints::

            Total snapshots: <n>
            <name1>
            <name2>
            ...

        Snapshot trees are presented as flat names; parent linkage is not
        available from the ``listSnapshots`` plain form, so :attr:`parent`
        is always ``None``.

        :param payload: The decoded stdout from ``vmrun``.

        :returns: A list of :class:`SnapshotRecord`, possibly empty.
        :raises VMWorkstationParseError: When the header line cannot be
            located or the declared count does not match the body.
    """
    if payload is None:
        text = ""
    else:
        text = payload

    raw_lines = text.splitlines()
    stripped_lines: List[str] = []
    for raw in raw_lines:
        stripped = raw.strip()
        if len(stripped) > 0:
            stripped_lines.append(stripped)

    if len(stripped_lines) == 0:
        rtnval: List[SnapshotRecord] = []
        return rtnval

    header = stripped_lines[0]
    lower_header = header.lower()
    if lower_header.startswith("total snapshots:") is False:
        err_msg_lines = ["Unexpected 'vmrun listSnapshots' header."]
        err_msg_lines.append("    HEADER: {!r}".format(header))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(message=err_msg, raw_output=text)

    count_text = header.split(":", 1)[1].strip()
    try:
        declared_count = int(count_text)
    except ValueError:
        err_msg_lines = ["Unable to parse snapshot count."]
        err_msg_lines.append("    COUNT_TEXT: {!r}".format(count_text))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(
            message=err_msg, raw_output=text,
        ) from None

    body_lines = stripped_lines[1:]
    if len(body_lines) != declared_count:
        err_msg_lines = [
            "Snapshot count mismatch between header and body.",
        ]
        err_msg_lines.append("    DECLARED: {}".format(declared_count))
        err_msg_lines.append("    ACTUAL: {}".format(len(body_lines)))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(message=err_msg, raw_output=text)

    records: List[SnapshotRecord] = []
    for body in body_lines:
        record = SnapshotRecord(name=body, parent=None)
        records.append(record)

    rtnval = records
    return rtnval


def parse_list_running(*, payload: str) -> List[str]:
    """
        Parse the stdout of ``vmrun list``.

        ``vmrun list`` prints::

            Total running VMs: <n>
            <vmx_path_1>
            <vmx_path_2>
            ...

        :param payload: The decoded stdout from ``vmrun``.

        :returns: A list of VMX paths, possibly empty.
        :raises VMWorkstationParseError: When the header line cannot be
            located or the declared count does not match the body.
    """
    if payload is None:
        text = ""
    else:
        text = payload

    raw_lines = text.splitlines()
    stripped_lines: List[str] = []
    for raw in raw_lines:
        stripped = raw.strip()
        if len(stripped) > 0:
            stripped_lines.append(stripped)

    if len(stripped_lines) == 0:
        rtnval: List[str] = []
        return rtnval

    header = stripped_lines[0]
    lower_header = header.lower()
    if lower_header.startswith("total running vms:") is False:
        err_msg_lines = ["Unexpected 'vmrun list' header."]
        err_msg_lines.append("    HEADER: {!r}".format(header))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(message=err_msg, raw_output=text)

    count_text = header.split(":", 1)[1].strip()
    try:
        declared_count = int(count_text)
    except ValueError:
        err_msg_lines = ["Unable to parse running VM count."]
        err_msg_lines.append("    COUNT_TEXT: {!r}".format(count_text))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(
            message=err_msg, raw_output=text,
        ) from None

    body_lines = stripped_lines[1:]
    if len(body_lines) != declared_count:
        err_msg_lines = [
            "Running VM count mismatch between header and body.",
        ]
        err_msg_lines.append("    DECLARED: {}".format(declared_count))
        err_msg_lines.append("    ACTUAL: {}".format(len(body_lines)))
        err_msg = os.linesep.join(err_msg_lines)
        raise VMWorkstationParseError(message=err_msg, raw_output=text)

    rtnval = list(body_lines)
    return rtnval


__all__ = [
    "SnapshotRecord",
    "parse_list_running",
    "parse_list_snapshots",
]
