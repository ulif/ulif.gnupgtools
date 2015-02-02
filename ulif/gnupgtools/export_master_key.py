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
"""Create key files needed for exporting GPG subkeys to other machines.

 Exports all public and secret keys of a chosen primary keypair, including
 subkeys (private and public parts) bound to this key.

 The three resulting files contain the public keys  (<key-id>.pub),
 all secret keys (<key-id>.priv) and the private keys except the
 primary secret key (<key-id>.subkeys).

 *Before* running this script you must create additional subkeys.
"""
import argparse
import grp
import os
import pkg_resources
import pwd
import re
import stat
import subprocess
import sys
import tarfile
import time
from io import BytesIO
from ulif.gnupgtools.utils import execute

#: Regular expression representing a hexadecimal number
RE_HEX_NUMBER = re.compile('(^[a-f0-9]+)$|(^[A-F0-9]+$)')

#: Flags to set for user read/write permissions (no group, nor others)
PERM_USER_RW_ONLY = stat.S_IRUSR | stat.S_IWUSR

input_func = input
if sys.version[0] < "3":
    input_func = raw_input  # pragma: no cover


VERSION = pkg_resources.get_distribution('ulif.gnupgtools').version


def s(text):
    """Turn `text` into a string.

    Mainly designed to turn binary strings in Python 3 into regular
    strings.

      >>> s('a')
      'a'
      >>> s(b'a')
      'a'

    Also lists of texts are supported:

      >>> s([b'list', 'entry'])
      ['list', 'entry']

    """
    if isinstance(text, list):
        return [s(x) for x in text]
    if not isinstance(text, str):
        text = text.decode('utf-8')
    return text


def create_tarfile(archive_name, members_dict):
    """Create a tar archive.

    The archive will be created as `archive_name`. `members_dict`
    should contain names (keys) and file contents (values).

    Currently we support only one level of files.

    All files are stored with user perms set only (no group or other
    permissions.)
    """
    tar = tarfile.open(archive_name, "w:gz")
    os.chmod(archive_name, PERM_USER_RW_ONLY)  # ~ octal 0600 ~ rw-------
    for name, content in members_dict.items():
        info = tarfile.TarInfo(name=name)
        info.mode = PERM_USER_RW_ONLY          # ~ octal 0600 = rw-------
        info.mtime = time.time()
        info.size = len(content)
        info.uid = os.getuid()
        info.gid = os.getgid()
        info.uname = pwd.getpwuid(os.getuid()).pw_name
        info.gname = grp.getgrgid(os.getgid()).gr_name
        tar.addfile(tarinfo=info, fileobj=BytesIO(content))
    tar.close()


def handle_options(args):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Export GnuPG master key")
    parser.add_argument('-p', '--path', dest="gnupg_path", default='gpg',
                        metavar='PATH', help='Path to GnuPG binary to use')
    args = parser.parse_args(args)
    return args


def greeting():
    """Startup message.
    """
    print(
        ("gpg-export-master-key.py %s; Copyright (C) 2014 Uli Fouquet. "
         "This is free software: you are free to change and redistribute "
         "it. There is NO WARRANTY, to the extent permitted by law. "
         ) % VERSION
        )


def get_secret_keys_output(gnupg_path='gpg'):
    """Get a list of all secret keys as output by GPG.

    Returns a tuple `(stdout, stderr)` containing output generated
    during command runtime.
    """
    return execute([gnupg_path, "-K"])


def get_key_list(gnupg_path='gpg'):
    """Parse gpg output to create a list of secret keys.
    """
    output, err = get_secret_keys_output(gnupg_path=gnupg_path)
    key_list = []
    curr_key = None
    curr_ids = []
    id_info = []
    for line in output.split(b"\n"):
        if line.startswith(b"sec"):
            if curr_key is not None:
                key_list.append((curr_ids, s(id_info), s(curr_key)))
            curr_ids = []
            id_info = line
            curr_key = line.split(b"/")[1].split(b" ")[0]
        elif line.startswith(b"uid"):
            uid = line[3:].strip()
            curr_ids.append(s(uid))
    if curr_key is not None:
        key_list.append((curr_ids, s(id_info), s(curr_key)))
    return sorted(key_list)


def output_key_list(key_list):
    """Output key list to screen.

    We expect a list of triples (ids, id_info, key) where `ids` is a
    list of uids bound to the given key, `id_info` is text describing
    the key and `key` is the short key as a hex number.

    The input is formatted somewhat 'nicely' for output.

    Example:

        >>> key_list = [
        ...   (['foo1', 'foo2'], 'bar', 'baz'),
        ...   (['boo'], 'far', 'bar'),
        ... ]
        >>> output_key_list(key_list)
        [  1] bar
              foo1
              foo2
        [  2] far
              boo

    """
    for num, list_entry in enumerate(key_list):
        ids, info, key = list_entry
        print("[%3d] %s" % (num + 1, info))
        for name in ids:
            print("      %s" % name)


def input_key(max_key):
    """Ask user for an entry.

    Returns a number or exits (with status 0, if the user types
    ``q``). The number is between ``1`` and `max_key`.
    """
    prompt_text = "Which key do you want to export? (1..%s; q to quit): " % (
        max_key)
    # pick an entry to process
    entry_num = None
    while entry_num is None:
        entry_num = input_func(prompt_text)
        if entry_num == "q":
            print("Okay, abort.")
            sys.exit(0)
        try:
            entry_num = int(entry_num)
        except ValueError:
            entry_num = 0
        if (entry_num < 1) or (entry_num > max_key):
            entry_num = None
    return entry_num


def export_keys(hex_id):
    """Export key wih id `hex_id`.

    Returns directory, where all exported data was written to.
    """
    hex_id = str(hex_id)
    if not RE_HEX_NUMBER.match(hex_id):
        raise ValueError('Not a valid hex number: %s' % hex_id)
    pub_path = "%s.pub" % hex_id
    priv_path = "%s.priv" % hex_id
    subs_path = "%s.subkeys" % hex_id
    tar_path = os.path.join(os.getcwd(), "%s.tar.gz" % hex_id)

    pub_file, err = execute(["gpg", "--export", "--armor", hex_id])
    print("Extract public keys to: %s" % (pub_path, ))

    priv_file, err = execute(
        ["gpg", "--export-secret-keys", "--armor", hex_id])
    print("Extract secret keys to: %s" % (priv_path))

    subs_file, err = execute(
        ["gpg", "--export-secret-subkeys", "--armor", hex_id])
    print("Extract subkeys belonging to this key to: %s" % (subs_path))

    create_tarfile(
        tar_path,
        {
            pub_path: pub_file,
            priv_path: priv_file,
            subs_path: subs_file}
        )
    print("\nAll export files written to: %s." % (tar_path))
    return tar_path


def main(args=sys.argv):
    options = handle_options(args[1:])
    greeting()
    key_list = get_key_list(gnupg_path=options.gnupg_path)
    print("Locally available keys (with secret parts available):")
    if len(key_list) == 0:
        print("No keys found. Exiting.")
        return
    output_key_list(key_list)
    max_key = len(key_list)
    entry_num = input_key(max_key)

    picked_hex_id = key_list[entry_num - 1][2]
    print("Picked key: %s (%s)" % (entry_num, key_list[entry_num - 1][2]))

    return export_keys(picked_hex_id)
