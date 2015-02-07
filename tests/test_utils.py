# Tests for ulif.gnupgtools.utils module
import os
import pytest
import tarfile
from ulif.gnupgtools.utils import execute, get_tmp_dir, tarfileopen


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


def test_tarfileopen(work_dir_creator):
    # we can open tarfiles with contextmanager, also in Python 2.6
    file1 = os.path.join(work_dir_creator.workdir, 'file1')
    file2 = os.path.join(work_dir_creator.workdir, 'file2')
    open(file1, 'w').write('file1')
    open(file2, 'w').write('file2')
    tmp_tar = None
    with tarfileopen('sample.tar.gz', 'w:gz') as tar:
        tar.add('file1')
        tar.add('file2')
        tmp_tar = tar
    assert tmp_tar.closed is True
    tar = tarfile.open('sample.tar.gz', 'r:gz')
    member_names = [x.name for x in tar.getmembers()]
    tar.close()
    assert sorted(member_names) == ['file1', 'file2']


def test_tarfileopen_w_exc(work_dir_creator):
    # tar files are closed in case of exceptions
    file1 = os.path.join(work_dir_creator.workdir, 'file1')
    file2 = os.path.join(work_dir_creator.workdir, 'file2')
    open(file1, 'w').write('file1')
    open(file2, 'w').write('file2')
    tmp_tar = None
    with pytest.raises(OSError):
        with tarfileopen('sample.tar.gz', 'w:gz') as tar:
            tmp_tar = tar
            tar.add('file1')
            tar.add('file2')
            tar.add('file3')
    assert tmp_tar.closed is True
