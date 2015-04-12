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
    parser.add_argument('-b', '--binary', dest="gnupg_path", default='gpg',
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


def keys_from_arch(path):
    """Turn archive at path into dict with predefined keys.

    Keys are ``'pub'``, ``'priv'``, ``'subkeys'``, and ``'key'``. The
    latter represents the master key's short fingerprint. The other
    items contain keys as exported from gpg.

    If keys are not consistend (i.e. we have 'AAAAAAA.pub' and
    'BBBBBBB.priv' in archive, a `ValueError` is raised.
    """
    archive_dict = extract_archive(path)
    result = dict()
    name = None
    for key, value in archive_dict.items():
        member_name, ext = os.path.splitext(key)
        for ext_name in ('.pub', '.priv', '.subkeys'):
            if ext != ext_name:
                continue
            if name is not None and member_name != name:
                raise ValueError('Key names in archive not consistent')
            name = member_name
            result[ext_name[1:]] = value
    result['key'] = name
    return result


def import_master_key(path, executable='gpg'):
    """Import master key from archive in `path`.

    Use `executable` as `gpg` binary.
    """
    keys_dict = keys_from_arch(path)
    out, err = None, None
    for key, opt in (('pub', '--import'),
                     ('subkeys', '--import')):
        with get_tmp_dir() as tmp_dir:
            infile_path = os.path.join(tmp_dir, 'key.%s' % key)
            with open(infile_path, 'wb') as fd:
                fd.write(keys_dict[key])
            out, err = execute([executable, opt, infile_path])
    return out, err


def main(args=sys.argv):
    options = handle_options(args[1:])
    if not is_valid_input_file(options.infile):
        print("Not a valid master key archive: %s" % options.infile,
              file=sys.stderr)
        sys.exit(2)
    import_master_key(options.infile)
    return
