import __builtin__
import os
import shutil
import tempfile
import unittest
from ulif.gnupgtools.export_master_key import (
    main, greeting, VERSION, get_secret_keys_output, get_key_list,
    export_keys, input_key,
    )


ORIG_RAW_INPUT = __builtin__.raw_input


class TestGPGExportMasterKeyTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self.old_env_gnupg_home = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = self.gnupg_home
        # setup fake raw_input
        self.fake_input_value = None  # returned by fake_raw_input
        __builtin__.raw_input = self.fake_raw_input

    def tearDown(self):
        __builtin__.raw_input = ORIG_RAW_INPUT   # restore mocked func.
        if self.old_env_gnupg_home is None:
            del os.environ['GNUPGHOME']
        else:
            os.environ['GNUPGHOME'] = self.old_env_gnupg_home
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def fake_raw_input(self, prompt=None):
        if prompt:
            print prompt,
        curr_value = self.fake_input_value[0]
        self.fake_input_value = self.fake_input_value[1:]
        print curr_value
        return curr_value

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

    def test_get_key_list(self):
        # we can get a list of secret keys
        self.create_sample_gnupg_home('two-users')
        result = get_key_list()
        assert result == [
            (
                ['Bob Tester <bob@example.org>'],
                'sec   2048R/DAA011C5 2015-01-06', 'DAA011C5'
                ),
            (
                ['Gnupg Testuser (no real person) <gnupg@example.org>',
                 'Gnupg Testuser (Other Identity) <gnupg@example.org>'],
                'sec   2048R/16FD1DE8 2015-01-06', '16FD1DE8'
                )
            ]

    def test_export_keys(self):
        # we can export a certain, existing key
        self.create_sample_gnupg_home('two-users')
        result_dir = export_keys('DAA011C5')
        assert os.path.isdir(result_dir)
        assert sorted(os.listdir(result_dir)) == [
            'DAA011C5.priv', 'DAA011C5.pub', 'DAA011C5.subkeys']

    def test_input_key(self):
        # we get a valid input key.
        self.fake_input_value = ["2", ]
        result = input_key(3)
        assert result == 2

    def test_input_key_non_numbers(self):
        # we do not accept non numbers
        self.fake_input_value = ["not-a-number", "2"]
        result = input_key(3)
        assert result == 2

    def test_input_key_min(self):
        # we must enter at least 1
        self.fake_input_value = ["0", "-1", "1", "2"]
        result = input_key(3)
        assert result == 1

    def test_input_key_max(self):
        # we allow at most the number passed in
        self.fake_input_value = ["12", "4", "3", "2"]
        result = input_key(3)
        assert result == 3

    def test_input_key_exit(self):
        # we can abort with 'q'
        self.fake_input_value = ["q"]
        self.assertRaises(
            SystemExit, input_key, 3)


def test_greeting(capsys):
    # in user greetings we tell about license and version
    greeting()
    out, err = capsys.readouterr()
    assert "free software" in out
    assert VERSION in out
