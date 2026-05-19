"""
    .. module:: guestcredential
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Guest credential carrier for ``vmrun`` guest-exec verbs.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass


@dataclass
class GuestCredential:
    """
        Username/password pair passed to ``vmrun -gu/-gp`` for guest-exec
        verbs (``runProgramInGuest``, ``copyFileFromHostToGuest``,
        ``copyFileFromGuestToHost``).

        :param username: Guest OS username.
        :param password: Guest OS password.
    """
    username: str
    password: str


__all__ = ["GuestCredential"]
