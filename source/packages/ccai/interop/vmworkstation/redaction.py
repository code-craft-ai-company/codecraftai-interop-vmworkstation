"""
    .. module:: redaction
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Argv redaction helpers for the VMware Workstation interop
                   client.

    The ``vmrun`` guest-exec subcommands accept the guest password on the
    command line via the ``-gp`` flag. The real argv must carry the
    plaintext password so the command can actually execute, but any copy of
    that argv that is stored on a result object, embedded in an exception,
    or written to a log must have the secret scrubbed.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List, Optional


_REDACTED_PLACEHOLDER = "<redacted>"
_SECRET_FLAGS = ("-gp",)


def redact_argv(*, argv: Optional[List[str]]) -> Optional[List[str]]:
    """
        Return a copy of ``argv`` with the value following any secret flag
        (currently ``-gp``, the guest password) replaced by a redaction
        placeholder.

        The original list is never mutated; the real argv used for dispatch
        is left intact.

        :param argv: The argv to redact, or ``None``.

        :returns: A redacted copy of ``argv``, or ``None`` when ``argv`` is
            ``None``.
    """
    if argv is None:
        rtnval: Optional[List[str]] = None
        return rtnval

    redacted: List[str] = []
    redact_next = False
    for token in argv:
        if redact_next is True:
            redacted.append(_REDACTED_PLACEHOLDER)
            redact_next = False
            continue

        redacted.append(token)
        if token in _SECRET_FLAGS:
            redact_next = True

    rtnval = redacted
    return rtnval


__all__ = ["redact_argv"]
