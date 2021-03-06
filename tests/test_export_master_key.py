import grp
import os
import pwd
import pytest
import shutil
import stat
import sys
import tarfile
import tempfile
import ulif.gnupgtools.export_master_key
from ulif.gnupgtools.utils import tarfile_open
from ulif.gnupgtools.export_master_key import (
    main, greeting, VERSION, get_secret_keys_output, get_key_list,
    export_keys, input_key, RE_HEX_NUMBER, create_tarfile, s
    )

try:
    ORIG_RAW_INPUT = raw_input           # python 2.x
except NameError:
    ORIG_RAW_INPUT = input               # python 3.x


class InputMock(object):
    """Mock for generic `raw_input` or `input` method.
    """

    fake_input_values = []

    def input_replacement(self, prompt=None):
        if not prompt:
            prompt = ''
        curr_value = self.fake_input_values[0]
        self.fake_input_values = self.fake_input_values[1:]
        print("%s%s" % (prompt, curr_value))
        return curr_value

    @classmethod
    def restore_raw_input(cls):
        ulif.gnupgtools.export_master_key.input_func = ORIG_RAW_INPUT


@pytest.fixture(scope="module")
def mock_input(request):
    mocker = InputMock()
    ulif.gnupgtools.export_master_key.input_func = mocker.input_replacement
    request.addfinalizer(mocker.restore_raw_input)
    return mocker


class TestInputKey(object):
    # tests for input_key function

    def test_input_key(self, mock_input):
        # we get a valid input key.
        mock_input.fake_input_values = ["2", ]
        result = input_key(3)
        assert result == 2

    def test_input_key_non_numbers(self, mock_input):
        # we do not accept non numbers
        mock_input.fake_input_values = ["not-a-number", "2"]
        result = input_key(3)
        assert result == 2

    def test_input_key_min(self, mock_input):
        # we must enter at least 1
        mock_input.fake_input_values = ["0", "-1", "1", "2"]
        result = input_key(3)
        assert result == 1

    def test_input_key_max(self, mock_input):
        # we allow at most the number passed in
        mock_input.fake_input_values = ["12", "4", "3", "2"]
        result = input_key(3)
        assert result == 3

    def test_input_key_exit(self, mock_input):
        # we can abort with 'q'
        mock_input.fake_input_values = ["q"]
        with pytest.raises(SystemExit):
            input_key(3)


class TestExportMasterKeyModule(object):
    # export_master_key module tests (except input_key, s. above)

    def test_RE_HEX_NUMBER(self):
        assert RE_HEX_NUMBER.match('abcdef0')
        assert RE_HEX_NUMBER.match('ABCDEF0')
        assert RE_HEX_NUMBER.match('0')
        assert not RE_HEX_NUMBER.match('0a1B2c')  # mixed case
        assert not RE_HEX_NUMBER.match('b"01234"')
        assert not RE_HEX_NUMBER.match('not-a-hex-num')
        assert not RE_HEX_NUMBER.match('')

    def test_text_substitution(self):
        # text substitution works
        assert s("text") == "text"
        assert s(b"text".decode("utf-8")) == "text"

    def test_create_tarfile(self, work_dir_creator):
        # we can create tarfiles
        create_tarfile(
            'sample.tar.gz',
            {
                'file1': b'content1',
                'file2': b'content2',
                })
        assert tarfile.is_tarfile('sample.tar.gz')
        with tarfile_open('sample.tar.gz', 'r:gz') as tar:
            tar.extractall()
        assert sorted(os.listdir(".")) == ['file1', 'file2', 'sample.tar.gz']
        assert open('file1', 'r').read() == 'content1'
        assert open('file2', 'r').read() == 'content2'
        expected_perm = stat.S_IRUSR | stat.S_IWUSR  # ~ rw-------
        assert stat.S_IMODE(os.stat('file1').st_mode) == expected_perm
        assert stat.S_IMODE(os.stat('file2').st_mode) == expected_perm
        assert stat.S_IMODE(os.stat('sample.tar.gz').st_mode) == expected_perm

    def test_create_tarfile_ids(self, work_dir_creator):
        # when creating tarfiles, uids and gids are set properly
        create_tarfile(
            'sample.tar.gz',
            {
                'file1': b'content1',
                'file2': b'content2',
                })
        assert tarfile.is_tarfile('sample.tar.gz')
        with tarfile_open('sample.tar.gz', 'r:gz') as tar:
            members = tar.getmembers()
        assert members[0].uid == os.getuid()
        assert members[1].uid == os.getuid()
        assert members[0].gid == os.getgid()
        assert members[1].gid == os.getgid()
        assert members[0].uname == pwd.getpwuid(os.getuid()).pw_name
        assert members[0].gname == grp.getgrgid(os.getgid()).gr_name

    def test_main_exists(self):
        # the main function exists
        assert main is not None

    def test_version(self):
        # we can get a version string
        assert VERSION is not None

    def test_greeting(self, capsys):
        # in user greetings we tell about license and version
        greeting()
        out, err = capsys.readouterr()
        assert "free software" in out
        assert VERSION in out

    def test_get_secret_keys_output(self, gnupg_home_creator):
        # we can get secret keys via gpg commandline tool
        gnupg_home_creator.create_sample_gnupg_home('one-secret')
        out, err = get_secret_keys_output()
        assert err is None
        assert out[-161:] == (
            b"----------------------\n"
            b"sec   2048R/16FD1DE8 2015-01-06\n"
            b"uid                  Gnupg Testuser (no real person) "
            b"<gnupg@example.org>\n"
            b"ssb   2048R/75DD62A6 2015-01-06\n"
            b"\n"
            )

    def test_get_secret_keys_output_gpg_path(
            self, fake_gpg_binary, gnupg_home_creator):
        # a passed-in GnuPG path is respected
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        out, err = get_secret_keys_output(gnupg_path=fake_gpg_binary.path)
        assert err is None
        assert b"Ferdinand Fake" in out

    def test_get_key_list(self, gnupg_home_creator):
        # we can get a list of secret keys
        gnupg_home_creator.create_sample_gnupg_home('two-users')
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

    def test_get_key_list_gpg_path(self, gnupg_home_creator, fake_gpg_binary):
        # Custom GnuPG paths are respected
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        result = get_key_list(gnupg_path=fake_gpg_binary.path)
        assert result == [
            (
                ['Ferdinand Fake <ferdi@fake.org>'],
                'sec   4096R/00000000 2014-05-23', '00000000'
                )
            ]

    def test_export_keys(self, gnupg_home_creator):
        # we can export a certain, existing key
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        result_path = export_keys('DAA011C5')
        assert os.path.isfile(result_path)
        assert os.path.basename(result_path) == 'DAA011C5.tar.gz'
        assert tarfile.is_tarfile(result_path)
        with tarfile_open(result_path, 'r:gz') as tar:
            members = tar.getmembers()
        priv_key_info = [
            x for x in members if x.name == 'DAA011C5.priv'][0]
        assert priv_key_info.size > 0
        return

    def test_export_keys_requires_valid_hex_num(self, gnupg_home_creator):
        with pytest.raises(ValueError) as exc_info:
            export_keys('not-a-hex')
        assert 'Not a valid hex number: not-a-hex' in exc_info.value.args

    def test_main(self, gnupg_home_creator, mock_input, capsys):
        # we can export keys via the main() function
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        mock_input.fake_input_values = ["1"]
        result_path = main(['gpg-export-master-key', ])
        out, err = capsys.readouterr()
        assert os.path.exists(result_path)
        assert result_path.startswith(gnupg_home_creator.workdir)
        assert tarfile.is_tarfile(result_path)
        with tarfile_open(result_path, 'r:gz') as tar:
            members = tar.getmembers()
        assert sorted([x.name for x in members]) == [
            'DAA011C5.priv', 'DAA011C5.pub', 'DAA011C5.subkeys']
        assert 0 not in [x.size for x in members]

    def test_main_empty(self, gnupg_home_creator, capsys):
        # we cope with empty gnupg homes
        gnupg_home_creator.create_sample_gnupg_home('empty')
        result = main(['gpg-export-master-key', ])
        out, err = capsys.readouterr()
        assert result is None
        assert "No keys found. Exiting." in out

    def test_main_option_binary_path(
            self, gnupg_home_creator, mock_input, capsys, fake_gpg_binary,):
        # we can set a custom gpg path
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        mock_input.fake_input_values = ["1"]
        main(['gpg-export-master-key', '-b', fake_gpg_binary.path])
        out, err = capsys.readouterr()
        assert "Ferdinand Fake <ferdi@fake.org>" in out

    @pytest.mark.skipif(not os.path.isfile("/usr/bin/gpg2"),
                        reason="No such file: '/usr/bin/gpg2'")
    def test_main_use_gpg2(self, gnupg_home_creator, mock_input,
                             capsys, fake_gpg_binary,):
        # we can use gpg2 if installed
        gnupg_home_creator.create_sample_gnupg_home('two-users')
        mock_input.fake_input_values = ["1"]
        main(['gpg-export-master-key', '-b', 'gpg2'])
        out, err = capsys.readouterr()
        assert "DAA011C5.tar.gz" in out

    def test_help(self, gnupg_home_creator, capsys):
        # we can get help
        with pytest.raises(SystemExit) as exc_info:
            main(["gpg-export-master-key", "--help"])
        assert exc_info.value.code == 0
        out, err = capsys.readouterr()
        out = out.replace(
            os.path.basename(sys.argv[0]), 'gpg-export-master-key')
        assert out == (
            'usage: gpg-export-master-key [-h] [-b PATH]\n'
            '\n'
            'Export GnuPG master key\n'
            '\n'
            'optional arguments:\n'
            '  -h, --help            show this help message and exit\n'
            '  -b PATH, --binary PATH\n'
            '                        Path to GnuPG binary to use\n'
            )
