# Tests for ulif.gnupgtools.utils module
import os
import pytest
from ulif.gnupgtools.utils import execute, get_tmp_dir


@pytest.mark.skipif(
    not os.path.exists('/bin/echo'), reason="needs /bin/echo")
def test_execute():
    # we can execute commands (w/o shell)
    cmd = ["/bin/echo", 'Hello $PATH']
    out, err = execute(cmd)
    assert out == b'Hello $PATH\n'

def test_get_tmp_dir():
    # we can create temporary dirs
    d = None
    with get_tmp_dir() as d:
        assert os.path.exists(d)
        assert os.path.isdir(d)
    assert not os.path.exists(d)

def test_get_tmp_dir_w_exc():
    # temp dirs are removed also in case of exceptions
    d = None
    with pytest.raises(Exception):
        with get_tmp_dir() as d:
            assert os.path.exists(d)
            raise Exception('Intented Exception')
    assert not os.path.exists(d)
