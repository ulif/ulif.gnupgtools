#
#    ulif.gnupgtools -- gnupg made less complex
#    Copyright (C) 2015  Uli Fouquet
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Import key files as exported by `gpg-export-master-key`.

 Imports all public and secret keys of a chosen primary keypair, including
 subkeys (private and public parts) bound to this key.
"""
from __future__ import print_function
import argparse
import os
import sys
import tarfile
from ulif.gnupgtools.utils import get_tmp_dir, execute


def handle_options(args):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Import GnuPG master key")
    parser.add_argument('infile', metavar='FILE',
                        help='tar.gz file created by gpg-export-master-key.')
    parser.add_argument('-p', '--path', dest="gnupg_path", default='gpg',
                        metavar='PATH', help='Path to GnuPG binary to use')
    opts = parser.parse_args(args)
    return opts


def is_valid_input_file(path):
    """Detect whether `path` leads to a valid input file.
    """
    if not path:
        return False
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return False
    if not tarfile.is_tarfile(path):
        return False
    return True


def extract_archive(path):
    """Turn tar archive at `path` into a dict.

    A few rules for archive files we accept:

    - File format must be ``.tar.gz``.
    - Only members with filename extension '.subkeys' | '.pub' | '.priv'
      are extracted.
    - Only regular files are extracted (no dirs, etc.)

    The archive is returned as a dict with member names as keys and
    file contents as value.
    """
    result = dict()
    tar = tarfile.open(path, "r:gz")
    for info in tar.getmembers():
        if not info.isfile():
            continue  # ignore non-regular files
        if os.path.split(info.name)[0] != "":
            continue  # ignore stuff in subdirs
        ext = os.path.splitext(info.name)[1]
        if ext not in ('.subkeys', '.priv', '.pub'):
            continue  # ignore files with unwanted filename extension
        result[info.name] = tar.extractfile(info).read()
    tar.close()
    return result


def import_master_key(path):
    archive_dict = extract_archive(path)
    out, err = None, None
    for name, content in archive_dict.items():
        if os.path.splitext(name)[1] == '.pub':
            with get_tmp_dir() as tmp_dir:
                infile_path = os.path.join(tmp_dir, name)
                with open(infile_path, 'wb') as fd:
                    fd.write(content)
                out, err = execute(['gpg', '--import', infile_path])
    return out, err


def main(args=sys.argv):
    options = handle_options(args[1:])
    if not is_valid_input_file(options.infile):
        print("Not a valid master key archive: %s" % options.infile,
              file=sys.stderr)
        sys.exit(2)
