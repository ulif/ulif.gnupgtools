import os
import pytest
import shutil
import tempfile


class WorkDirCreator(object):

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self._old_cwd = os.getcwd()
        os.mkdir(self.workdir)
        os.chdir(self.workdir)

    def tear_down(self):
        os.chdir(self._old_cwd)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class GnuPGHomeCreator(WorkDirCreator):

    def __init__(self):
        super(GnuPGHomeCreator, self).__init__()
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self._old_env = os.environ.copy()
        os.environ['GNUPGHOME'] = self.gnupg_home

    def tear_down(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        super(GnuPGHomeCreator, self).tear_down()

    def create_sample_gnupg_home(self, name):
        # create a gnupg sample config in self.gnupg_home
        # name must be one of the subdirs in `gnupg-samples/`.
        sample_home = os.path.join(
            os.path.dirname(__file__), 'gnupg-samples', name)
        shutil.copytree(sample_home, self.gnupg_home)


@pytest.fixture(scope="function")
def work_dir_creator(request):
    creator = WorkDirCreator()
    request.addfinalizer(creator.tear_down)
    return creator


@pytest.fixture(scope="function")
def gnupg_home_creator(request):
    creator = GnuPGHomeCreator()
    request.addfinalizer(creator.tear_down)
    return creator
