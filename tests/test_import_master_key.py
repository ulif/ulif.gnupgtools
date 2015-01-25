import os
import pytest
import sys
from ulif.gnupgtools.import_master_key import handle_options, main

class TestArgParser(object):

    def test_help(self, capsys):
        # we support --help
        with pytest.raises(SystemExit) as exc_info:
            handle_options(['foo', '--help'])
        out, err = capsys.readouterr()
        out = out.replace(
            os.path.basename(sys.argv[0]), 'gpg-import-master-key')
        assert out == (
            "usage: gpg-import-master-key [-h] [-p PATH]\n"
            "\n"
            "Import GnuPG master key\n"
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
        out = out.replace(
            os.path.basename(sys.argv[0]), 'gpg-import-master-key')
        assert out == (
            'usage: gpg-import-master-key [-h] [-p PATH]\n'
            '\n'
            'Import GnuPG master key\n'
            '\n'
            'optional arguments:\n'
            '  -h, --help            show this help message and exit\n'
            '  -p PATH, --path PATH  Path to GnuPG binary to use\n'
            )
