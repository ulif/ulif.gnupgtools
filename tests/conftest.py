import os
import pytest
import shutil
import stat
import sys
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


class ExecutableScript(object):
    """Creates/removes an executable script.

    Installs (and removes) an executable script from a template.

    The tempate is looked up by `template_name` in the local test dir and
    must provide a placeholder (``%s``) which will be replaced with
    Python executable used at test time.

    The generated script is then copied to a temporary directory and
    made executable by setting approriate flags. The script basename
    will be like `template_name` except if you gave a different
    `script_name` as well.

    The one interesting part you normally need, is the `path`
    attribute containing the path to the generated script.
    """
    def __init__(self, template_name, script_name=None):
        self.template_name = template_name
        self.script_name = script_name or self.template_name

    def install(self):
        """Install script from template.
        """
        self._tmpdir = tempfile.mkdtemp()
        template_path = os.path.join(
            os.path.dirname(__file__), self.template_name)
        source = open(template_path, 'r').read()
        source = source % (sys.executable, )
        self.path = os.path.join(self._tmpdir, self.script_name)
        with open(self.path, 'w') as fd:
            fd.write(source)
        # set strict permissions on Unix
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    def remove(self):
        shutil.rmtree(self._tmpdir)


@pytest.fixture(scope="module")
def fake_gpg_binary(request):
    fake_binary = ExecutableScript('gpg_fake')
    request.addfinalizer(fake_binary.remove)
    fake_binary.install()
    return fake_binary


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
