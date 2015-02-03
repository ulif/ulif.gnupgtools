# Tests for ulif.gnupgtools.utils module
import pytest
from ulif.gnupgtools.utils import execute


def test_execute():
    # we can execute commands (w/o shell)
    cmd = ["/bin/echo", 'Hello $PATH']
    out, err = execute(cmd)
    assert out == b'Hello $PATH\n'
