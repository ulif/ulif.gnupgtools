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
"""Helpers needed by at least two other modules.
"""
import shutil
import subprocess
import tarfile
import tempfile
from contextlib import contextmanager


def execute(cmd_list):
    """Execute the command in `cmd_list`.

    `cmd_list` must be a list of arguments as entered, for instance,
    on the shell.  Returns (stdout, stderr) output.
    """
    proc = subprocess.Popen(
        cmd_list, stdout=subprocess.PIPE, shell=False)
    output, err = proc.communicate()
    return output, err


@contextmanager
def get_tmp_dir():
    """Get a temporary directory.

    This contextmanager creates a temporary directory that can be used
    with a `with` statement.  The directory (and any content) is
    removed afterwards.

    Returns a string containing the path to the temporary directory.
    """
    directory = tempfile.mkdtemp()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


@contextmanager
def tarfile_open(*args):
    """Replacement for the original tarfile context manager, which is
    not available in Python2.6.

    You can use it like `tarfile.open()`.
    """
    tar = tarfile.open(*args)
    try:
        yield tar
    finally:
        tar.close()
