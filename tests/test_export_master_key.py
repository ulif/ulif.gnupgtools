import os
import shutil
import tempfile
import unittest
import ulif.gnupgtools
from ulif.gnupgtools import export_master_key
from ulif.gnupgtools.export_master_key import main, greeting, VERSION


class TestGPGExportMasterKeyTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self.old_env_gnupg_home = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = self.gnupg_home

    def tearDown(self):
        if self.old_env_gnupg_home is None:
            del os.environ['GNUPGHOME']
        else:
            os.environ['GNUPGHOME'] = self.old_env_gnupg_home
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_main_exists(self):
        # the main function exists
        assert main is not None

    def test_version(self):
        # we can get a version string
        assert VERSION is not None


def test_greeting(capsys):
    # in user greetings we tell about license and version
    greeting()
    out, err = capsys.readouterr()
    assert "free software" in out
    assert VERSION in out
