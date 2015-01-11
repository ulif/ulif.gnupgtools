try:
    import builtins                 # python 3.x
except ImportError:
    import __builtin__ as builtins  # python 2.x
import os
import pytest
import shutil
import tempfile
import unittest
from ulif.gnupgtools.export_master_key import (
    main, greeting, VERSION, get_secret_keys_output, get_key_list,
    export_keys, input_key,
    )

try:
    ORIG_RAW_INPUT = builtins.raw_input  # python 2.x
except AttributeError:
    ORIG_RAW_INPUT = builtins.input      # python 3.x


class InputMock(object):
    """Mock for generic `raw_input` or `input` method.
    """

    fake_input_values = []

    def input_replacement(self, prompt=None):
        if prompt:
            print(prompt, )
        curr_value = self.fake_input_values[0]
        self.fake_input_values = self.fake_input_values[1:]
        print(curr_value)
        return curr_value

    @classmethod
    def restore_raw_input(cls):
        builtins.raw_input = ORIG_RAW_INPUT


@pytest.fixture(scope="module")
def mock_input(request):
    mocker = InputMock()
    builtins.raw_input = mocker.input_replacement
    request.addfinalizer(mocker.restore_raw_input)
    return mocker


class GnuPGHomeCreator(object):

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self._old_env = os.environ.copy()

    def tear_down(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.environ.clear()
        os.environ.update(self._old_env)

    def create_sample_gnupg_home(self, name):
        # create a gnupg sample config in self.gnupg_home
        # name must be one of the subdirs in `gnupg-samples/`.
        sample_home = os.path.join(
            os.path.dirname(__file__), 'gnupg-samples', name)
        shutil.copytree(sample_home, self.gnupg_home)


@pytest.fixture(scope="function")
def gnupg_home_creator(request):
    creator = GnuPGHomeCreator()
    request.addfinalizer(creator.tear_down)
    return creator


class TestGPGExportMasterKeyTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self.old_env_gnupg_home = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = self.gnupg_home
        # setup fake raw_input
        self.fake_input_value = None  # returned by fake_raw_input
        builtins.raw_input = self.fake_raw_input

    def tearDown(self):
        builtins.raw_input = ORIG_RAW_INPUT   # restore mocked func.
        if self.old_env_gnupg_home is None:
            del os.environ['GNUPGHOME']
        else:
            os.environ['GNUPGHOME'] = self.old_env_gnupg_home
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def fake_raw_input(self, prompt=None):
        # this raw_input() replacement fakes input of the values
        # stored in self.fake_input_value.
        if prompt:
            print(prompt, )
        curr_value = self.fake_input_value[0]
        self.fake_input_value = self.fake_input_value[1:]
        print(curr_value)
        return(curr_value)

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
            b"/gnupghome/secring.gpg\n"
            b"------------------------------------\n"
            b"sec   2048R/16FD1DE8 2015-01-06\n"
            b"uid                  Gnupg Testuser (no real person) "
            b"<gnupg@example.org>\n"
            b"ssb   2048R/75DD62A6 2015-01-06\n"
            b"\n"
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
        shutil.rmtree(result_dir)

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


def test_input_key_non_numbers(mock_input, capsys):
    # we do not accept non numbers
    mock_input.fake_input_values = ["not-a-number", "2"]
    result = input_key(3)
    assert result == 2


def test_export_keys(gnupg_home_creator):
    # we can export a certain, existing key
    gnupg_home_creator.create_sample_gnupg_home('two-users')
    result_dir = export_keys('DAA011C5')
    assert os.path.isdir(result_dir)
    assert sorted(os.listdir(result_dir)) == [
        'DAA011C5.priv', 'DAA011C5.pub', 'DAA011C5.subkeys']
    shutil.rmtree(result_dir)  # clean up
