# Create key files needed for exporting GPG subkeys to other machines.
#
# Exports all public and secret keys of a chosen primary keypair, including
# subkeys (private and public parts) bound to this key.
#
# The three resulting files contain the public keys  (<key-id>.pub),
# all secret keys (<key-id>.priv) and the private keys except the
# primary secret key (<key-id>.subkeys).
#
#
# *Before* running this script you must create additional subkeys.
#
import os
import pkg_resources
import subprocess
import sys
import tempfile


input_func = input
if sys.version[0] < "3":
    input_func = raw_input  # pragma: no cover


VERSION = pkg_resources.get_distribution('ulif.gnupgtools').version


def greeting():
    """Startup message.
    """
    print(
        ("gpg-export-master-key.py %s; Copyright (C) 2014 Uli Fouquet. "
           "This is free software: you are free to change and redistribute "
           "it. There is NO WARRANTY, to the extent permitted by law. "
         ) % VERSION
        )


def get_secret_keys_output():
    """Get a list of all secret keys as output by GPG.
    """
    print("Locally available keys (with secret parts available):")

    proc = subprocess.Popen(["gpg -K", ], stdout=subprocess.PIPE,
                            shell=True)
    output, err = proc.communicate()
    return output, err


def get_key_list():
    """Parse gpg output to create a list of secret keys.
    """
    output, err = get_secret_keys_output()
    key_list = []
    curr_key = None
    curr_ids = []
    id_info = []
    for line in output.split(b"\n"):
        if line.startswith(b"sec"):
            if curr_key is not None:
                key_list.append((curr_ids, id_info, curr_key))
            curr_ids = []
            id_info = line
            curr_key = line.split(b"/")[1].split(b" ")[0]
        elif line.startswith(b"uid"):
            uid = line[3:].strip()
            curr_ids.append(uid)
    if curr_key is not None:
        key_list.append((curr_ids, id_info, curr_key))
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
    tmp_dir = tempfile.mkdtemp()
    pub_path = os.path.join(tmp_dir, "%s.pub" % hex_id)
    priv_path = os.path.join(tmp_dir, "%s.priv" % hex_id)
    subs_path = os.path.join(tmp_dir, "%s.subkeys" % hex_id)

    cmd = "gpg --export --armor %s > %s" % (
        hex_id, pub_path)
    os.system(cmd)
    print("Exported public key to: %s" % (pub_path, ))

    cmd = "gpg --export-secret-keys --armor %s > %s" % (
        hex_id, priv_path)
    os.system(cmd)
    print("Exported secret keys to: %s" % (priv_path))

    cmd = "gpg --export-secret-subkeys --armor %s > %s" % (
        hex_id, subs_path)
    os.system(cmd)
    print("Exported subkeys belonging to this key to: %s" % (subs_path))

    print(
        "Copy these three files to your not-so-secure machine and"
        "import them (`gpg --import %s.pub %s.priv`)." % (
            hex_id, hex_id)
        )

    print()
    print("All export files written to directory %s." % (tmp_dir))
    return tmp_dir


def main():
    greeting()
    key_list = get_key_list()
    output_key_list(key_list)
    max_key = len(key_list)
    entry_num = input_key(max_key)

    picked_hex_id = key_list[entry_num - 1][2]
    print("Picked key: ", entry_num, key_list[entry_num - 1][2])

    return export_keys(picked_hex_id)
