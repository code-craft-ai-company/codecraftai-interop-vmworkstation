"""
    .. module:: mockcommandrunner
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: A minimal ICommandRunner stand-in keyed on argv tuples.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Callable, Dict, List, Optional, Tuple

from ccai.interfaces.icommandrunner import RunResult


class MockCommandRunner:
    """
        Mock :class:`ICommandRunner` implementation that returns seeded
        :class:`RunResult` values for known argv tuples.

        :param responses: Mapping from argv tuple (e.g.
            ``("vmrun", "-T", "ws", "start", "/x.vmx", "nogui")``) to a
            :class:`RunResult`.
        :param default: Result returned when no exact argv match is found.
            ``None`` raises :class:`AssertionError` on miss.
    """

    def __init__(
        self,
        *,
        responses: Optional[Dict[Tuple[str, ...], RunResult]] = None,
        default: Optional[RunResult] = None,
    ) -> None:
        if responses is None:
            self._responses: Dict[Tuple[str, ...], RunResult] = {}
        else:
            self._responses = dict(responses)
        self._default: Optional[RunResult] = default
        self._calls: List[Tuple[List[str], Dict[str, object]]] = []
        return

    def seed(
        self,
        *,
        argv: List[str],
        result: RunResult,
    ) -> None:
        """
            Seed a response for an exact argv match.

            :param argv: Argv to match against.
            :param result: Result to return.
        """
        key = tuple(argv)
        self._responses[key] = result
        return

    @property
    def calls(self) -> List[Tuple[List[str], Dict[str, object]]]:
        """
            Captured calls as ``(argv, kwargs)`` tuples.
        """
        rtnval = self._calls
        return rtnval

    def run(
        self,
        args: List[str],
        *,
        elevated: bool = False,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        stdin: Optional[str] = None,
        timeout: Optional[float] = None,
        on_output: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        capture_output: bool = True,
    ) -> RunResult:
        """
            Look up the seeded response for ``args``.

            :param args: Argv being dispatched.

            :returns: The seeded :class:`RunResult`.
            :raises AssertionError: When no response and no default are
                seeded.
        """
        kwargs: Dict[str, object] = {
            "elevated": elevated,
            "cwd": cwd,
            "env": env,
            "stdin": stdin,
            "timeout": timeout,
            "capture_output": capture_output,
        }
        self._calls.append((list(args), kwargs))

        key = tuple(args)
        if key in self._responses:
            rtnval = self._responses[key]
            return rtnval

        if self._default is not None:
            rtnval = self._default
            return rtnval

        raise AssertionError(
            "MockCommandRunner: no seeded response for argv {!r}".format(
                list(args),
            ),
        )


__all__ = ["MockCommandRunner"]
