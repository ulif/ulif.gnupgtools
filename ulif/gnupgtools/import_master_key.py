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
import argparse
import os
import sys
import tarfile


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

    Returns a status and a textual reason: `(<bool>, <string>)`. If
    things are okay (path is valid), the reason is empty.

       >>> is_valid_input_file('/not-valid')
       (False, 'no such file')

    """
    if not path:
        return (False, 'no such file')
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return (False, 'no such file')
    if not tarfile.is_tarfile(path):
        return (False, 'not a tar archive')
    return (True, None)


def main(args=sys.argv):
    options = handle_options(args[1:])
