import os
import pytest
import shutil
import sys
from ulif.gnupgtools.utils import execute, tarfile_open
from ulif.gnupgtools.import_master_key import (
    handle_options, main, is_valid_input_file, extract_archive,
    keys_from_arch, import_master_key,
    )


def normalize_bin_path(text):
    """Replace binary path in `text` with 'gpg-import-master-key'.
    """
    return text.replace(
        os.path.basename(sys.argv[0]), 'gpg-import-master-key')


class TestArgParser(object):

    def test_file(self):
        # we can get a filename from options
        args = handle_options(['path-to-file', ])
        assert args.infile == 'path-to-file'

    def test_file_required(self, capsys):
        # we require an input file
        with pytest.raises(SystemExit) as exc_info:
            handle_options([])
        out, err = capsys.readouterr()
        err = normalize_bin_path(err)
        if isinstance(exc_info.value, int):
            assert exc_info.value is not 0  # Python 2.6
        else:
            assert exc_info.value.code != 0
        assert (
            ('following arguments are required: FILE' in err)
            or ('too few arguments' in err)
            )

    def test_help(self, capsys):
        # we support --help
        with pytest.raises(SystemExit) as exc_info:
            handle_options(['foo', '--help'])
        out, err = capsys.readouterr()
        out = normalize_bin_path(out)
        assert exc_info.value.code == 0
        assert out == (
            "usage: gpg-import-master-key [-h] [-b PATH] FILE\n"
            "\n"
            "Import GnuPG master key\n"
            "\n"
            "positional arguments:\n"
            "  FILE                  tar.gz file created by "
            "gpg-export-master-key.\n"
            "\noptional arguments:\n"
            "  -h, --help            show this help message and exit\n"
            "  -b PATH, --binary PATH\n"
            "                        Path to GnuPG binary to use\n"
            )

    def test_binary(self, capsys):
        # we support --binary
        options = handle_options(['-b', 'foo', 'path-to-file'])
        assert options.gnupg_path == 'foo'

    def test_binary_default(self):
        # we get a sensible default.
        options = handle_options(['path-to-file'])
        assert options.gnupg_path == 'gpg'


class TestImportMasterKeyModule(object):

    def create_tarfile(self, name, path):
        old_wd = os.getcwd()
        os.chdir(path)
        filenames = os.listdir(path)
        with tarfile_open(name, 'w:gz') as tar:
            for filename in filenames:
                if name.startswith('.') or (filename == name):
                    continue
                tar.add(filename)
        os.chdir(old_wd)
        return os.path.join(path, name)

    def test_help(self, capsys):
        # we can get help
        with pytest.raises(SystemExit) as exc_info:
            main(["gpg-import-master-key", "--help"])
        assert exc_info.value.code == 0
        out, err = capsys.readouterr()
        out = normalize_bin_path(out)
        assert out == (
            'usage: gpg-import-master-key [-h] [-b PATH] FILE\n'
            '\n'
            'Import GnuPG master key\n'
            '\n'
            'positional arguments:\n'
            '  FILE                  tar.gz file created by '
            'gpg-export-master-key.\n'
            '\n'
            'optional arguments:\n'
            '  -h, --help            show this help message and exit\n'
            '  -b PATH, --binary PATH\n'
            '                        Path to GnuPG binary to use\n'
            )

    def test_valid_input_not_a_file(self):
        # `None` is not considered a valid input file
        assert is_valid_input_file(None) is False
        # empty strings cannot be a valid path
        assert is_valid_input_file('') is False
        # not existing files are detected
        assert is_valid_input_file('/PrObAbLyNoTeXiStInG') is False
        assert is_valid_input_file('/foo/bar/baz') is False

    def test_valid_input_not_an_archive(self, work_dir_creator):
        # we can detect whether input files are tar archives
        sample_path = os.path.join(work_dir_creator.workdir, 'sample')
        with open(sample_path, 'w') as fd:
            fd.write('not-a-tar-gz-archive')
        assert is_valid_input_file(sample_path) is False

    def test_valid_input(self):
        # any valid tar archive is accepted
        sample_path = os.path.join(
            os.path.dirname(__file__), 'export-samples',
            'DAA011C5.tar.gz')
        assert is_valid_input_file(sample_path) is True

    def test_extract_archive(self, work_dir_creator):
        # we can extract archives
        src_path = os.path.join(
            os.path.dirname(__file__), 'export-samples',
            'DAA011C5.tar.gz')
        dest_path = os.path.join(
            work_dir_creator.workdir, 'sample.tar.gz')
        shutil.copy2(src_path, dest_path)
        result = extract_archive(dest_path)
        assert isinstance(result, dict)
        assert sorted(result.keys()) == [
            'DAA011C5.priv', 'DAA011C5.pub', 'DAA011C5.subkeys']
        assert result['DAA011C5.pub'].startswith(
            b'-----BEGIN PGP PUBLIC KEY BLOCK-----\n')

    def test_extract_archive_ignore_unwanted(self, work_dir_creator):
        # we ignore unwanted archive members
        path = 'sample.tgz'
        os.mkdir('foodir')
        for name in ('foo', 'bar.pub', 'foodir/baz.priv'):
            with open(name, 'w') as fd:
                fd.write('%s content' % name)
        with tarfile_open(path, 'w:gz') as tar:
            for name in ('foo', 'bar.pub', 'foodir'):
                tar.add(name)
        result = extract_archive(path)
        assert sorted(result.keys()) == ['bar.pub']
        assert result['bar.pub'] == b'bar.pub content'

    def test_keys_from_arch(self):
        # we can get key data from key archive
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        result = keys_from_arch(path)
        assert 'key' in result.keys()
        assert 'pub' in result.keys()
        assert 'priv' in result.keys()
        assert 'subkeys' in result.keys()

    def test_keys_from_arch_inconsistent(self, work_dir_creator):
        # we do not accept several key names
        path1 = os.path.join(work_dir_creator.workdir, '01020304.pub')
        path2 = os.path.join(work_dir_creator.workdir, 'FFFFFFFF.priv')
        open(path1, 'w').write('file1: 01020304.pub')
        open(path2, 'w').write('file2: FFFFFFFF.priv')
        tar_path = self.create_tarfile(
            'sample.tar.gz', work_dir_creator.workdir)
        with pytest.raises(ValueError):
            keys_from_arch(tar_path)

    def test_import_master_key(self, gnupg_home_creator, capsys):
        # we can import valid master keys
        gnupg_home_creator.create_sample_gnupg_home('one-secret')
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        import_master_key(path)
        out, err = execute(['gpg', '-K', 'DAA011C5'])
        assert b"DAA011C5" in out  # imported public key present
        assert b'sec#' in out      # imported master key not able to sign

    def test_import_master_key_respects_executable(
            self, gnupg_home_creator, capsys):
        # if we pass in an invalid executable path, we cause trouble
        # (which shows: the path is really tried to be used)
        gnupg_home_creator.create_sample_gnupg_home('one-secret')
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        with pytest.raises(OSError):
            import_master_key(path, executable="invalid-binary-path")

    def test_main_invalid_input(self, capsys):
        # we do not accept invalid input archives
        with pytest.raises(SystemExit) as exc_info:
            main(['gpg-import-master-key', '/invalid-path'])
        if isinstance(exc_info.value, int):
            assert exc_info.value is not 0  # Python 2.6
        else:
            assert exc_info.value.code != 0
        out, err = capsys.readouterr()
        err = normalize_bin_path(err)
        assert err == 'Not a valid master key archive: /invalid-path\n'

    def test_main(self, gnupg_home_creator, capsys):
        # we can import regular files
        gnupg_home_creator.create_sample_gnupg_home('one-secret')
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        main(['gpg-import-masterkey', path])
        out, err = execute(['gpg', '-K', 'DAA011C5'])
        assert b"DAA011C5" in out  # imported public key present
        assert b'sec#' in out      # imported master key not able to sign

    def test_main_option_binary(
            self, gnupg_home_creator, capsys, output_args_script):
        # we can set a custom gpg path
        gnupg_home_creator.create_sample_gnupg_home('empty')
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        main(['gpg-import-master-key', '-b', output_args_script.path, path])
        result_path = output_args_script.out_path
        assert os.path.exists(result_path)   # the output file was written

    @pytest.mark.skipif(not os.path.isfile("/usr/bin/gpg2"),
                        reason="No such file: '/usr/bin/gpg2'")
    def test_main_use_gpg2(self, gnupg_home_creator, capsys):
        # we can use gpg2 if installed
        gnupg_home_creator.create_sample_gnupg_home('one-secret')
        path = os.path.join(
            os.path.dirname(__file__), 'export-samples', 'DAA011C5.tar.gz')
        main(['gpg-import-masterkey', path, '-b', 'gpg2'])
        out, err = execute(['gpg', '-K', 'DAA011C5'])
        assert b"DAA011C5" in out  # imported public key present
        assert b'sec#' in out      # imported master key not able to sign
