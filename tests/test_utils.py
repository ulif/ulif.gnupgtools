# Tests for ulif.gnupgtools.utils module
import os
import pytest
from ulif.gnupgtools.utils import execute


@pytest.mark.skipif(
    not os.path.exists('/bin/echo'), reason="needs /bin/echo")
def test_execute():
    # we can execute commands (w/o shell)
    cmd = ["/bin/echo", 'Hello $PATH']
    out, err = execute(cmd)
    assert out == b'Hello $PATH\n'
