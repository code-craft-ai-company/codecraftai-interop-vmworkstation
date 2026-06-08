"""
    Pytest bootstrap: add the testroots tree to ``sys.path`` so test-only
    helpers under ``ccai.tests.*`` (PEP 420 namespace) resolve without
    requiring an editable install.
"""

import os
import sys


_HERE = os.path.dirname(os.path.abspath(__file__))
_TESTROOT = os.path.join(_HERE, "source", "testroots", "testbase")

if _TESTROOT not in sys.path:
    sys.path.insert(0, _TESTROOT)
