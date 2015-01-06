import os
import shutil
import tempfile
import unittest
from ulif.gnupgtools.export_master_key import (
    main, greeting, VERSION, get_secret_keys_output,
    )


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

    def create_sample_gnupg_home(self, name):
        # create a gnupg sample config in self.gnupg_home
        # name must be one of the subdirs in `gnupg-samples/`.
        sample_home = os.path.join(
            os.path.dirname(__file__), 'gnupg-samples', name)
        shutil.copytree(sample_home, self.gnupg_home)

    def test_main_exists(self):
        # the main function exists
        assert main is not None

    def test_version(self):
        # we can get a version string
        assert VERSION is not None

    def test_get_secret_keys_output(self):
        # we can get secret keys via gpg commandline tool
        self.create_sample_gnupg_home('one-secret')
        out, err = get_secret_keys_output()
        assert err is None
        assert out[-198:] == (
            "/gnupghome/secring.gpg\n"
            "------------------------------------\n"
            "sec   2048R/16FD1DE8 2015-01-06\n"
            "uid                  Gnupg Testuser (no real person) "
            "<gnupg@example.org>\n"
            "ssb   2048R/75DD62A6 2015-01-06\n"
            "\n"
            )


def test_greeting(capsys):
    # in user greetings we tell about license and version
    greeting()
    out, err = capsys.readouterr()
    assert "free software" in out
    assert VERSION in out
