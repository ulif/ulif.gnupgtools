import os
import pytest
import sys
from ulif.gnupgtools.import_master_key import (
    handle_options, main, is_valid_input_file,
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
        assert exc_info.value.code != 0  # signal an error to outside
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
            "usage: gpg-import-master-key [-h] [-p PATH] FILE\n"
            "\n"
            "Import GnuPG master key\n"
            '\n'
            'positional arguments:\n'
            '  FILE                  tar.gz file created by '
                                    'gpg-export-master-key.\n'
            "\noptional arguments:\n"
            "  -h, --help            show this help message and exit\n"
            "  -p PATH, --path PATH  Path to GnuPG binary to use\n"
            )


class TestImportMasterKeyModule(object):

    def test_help(self, capsys):
        # we can get help
        with pytest.raises(SystemExit) as exc_info:
            main(["gpg-import-master-key", "--help"])
        assert exc_info.value.code == 0
        out, err = capsys.readouterr()
        out = normalize_bin_path(out)
        assert out == (
            'usage: gpg-import-master-key [-h] [-p PATH] FILE\n'
            '\n'
            'Import GnuPG master key\n'
            '\n'
            'positional arguments:\n'
            '  FILE                  tar.gz file created by '
                                    'gpg-export-master-key.\n'
            '\n'
            'optional arguments:\n'
            '  -h, --help            show this help message and exit\n'
            '  -p PATH, --path PATH  Path to GnuPG binary to use\n'
            )

    def test_valid_input_not_a_file(self):
        # `None` is not considered a valid input file
        assert is_valid_input_file(None) == (
            False, 'no such file')
        # empty strings cannot be a valid path
        assert is_valid_input_file('') == (
            False, 'no such file')
        # not existing files are detected
        assert is_valid_input_file('/PrObAbLyNoTeXiStInG') == (
            False, 'no such file')
        assert is_valid_input_file('/foo/bar/baz') == (
            False, 'no such file')

    def test_valid_input_not_an_archive(self, work_dir_creator):
        # we can detect whether input files are tar archives
        sample_path = os.path.join(work_dir_creator.workdir, 'sample')
        with open(sample_path, 'w') as fd:
            fd.write('not-a-tar-gz-archive')
        assert is_valid_input_file(sample_path) == (
            False, 'not a tar archive')

    def test_valid_input(self, work_dir_creator):
        # any valid tar archive is accepted
        sample_path = os.path.join(
            os.path.dirname(__file__), 'export-samples',
            'DAA011C5.tar.gz')
        assert is_valid_input_file(sample_path) == (True, None)
