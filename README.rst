ulif.gnupgtools -- GnuPG easy
=============================

Commandline tools to ease some of the more complex operations possible
with GnuPG.


|build-status|_

.. |build-status| image:: https://travis-ci.org/ulif/ulif.gnupgtools.png?branch=master
.. _build-status: https://travis-ci.org/ulif/ulif.gnupgtools

Requires only Python (versions 2.6 to 3.3 supported) and GnuPG installed.

The package currently provides the following commandline tools:

  - ``export_master_key``
          Export a local master key to an archive file for import on a
          remote machine.


Resources
=========

`ulif.gnupgtools` are hosted on

  https://github.com/ulif/ulif.gnupgtools

The documentation can be found at

  https://ulif-gnupgtools.readthedocs.org/en/latest/

.. contents::

.. testsetup::
   :hide:

   from ulif.gnupgtools.testing import doctest_setup
   doctest_setup()

Examples
========

Create an export of a secret master key::

  $ gpg-export-master-key
  gpg-export-master-key 0.1.dev0; Copyright (C) 2014 Uli Fouquet.
  This is free software: you are free to change and redistribute it.
  There is NO WARRANTY, to the extent permitted by law.
  Locally available keys (with secret parts available):
  [  1] sec   2048R/DAA011C5 2015-01-06
        b'Bob Tester <bob@example.org>'
  [  2] sec   2048R/16FD1DE8 2015-01-06
        b'Gnupg Testuser (no real person) <gnupg@example.org>'
        b'Gnupg Testuser (Other Identity) <gnupg@example.org>'
  Which key do you want to export? (1..2; q to quit): 1
  Picked key: 1 (DAA011C5)
  Extract public keys to: DAA011C5.pub
  Extract secret keys to: DAA011C5.priv
  Extract subkeys belonging to this key to: DAA011C5.subkeys

  All export files written to: /.../DAA011C5.tar.gz.


Install
=======

`ulif.gnupgtools` can be installed via `pip`::

    $ pip install ulif.gnupgtools

Afterwards all commanline tools included should be available.


Developer Install
=================

It is recommended to setup sources in a virtual environment::

  $ virtualenv py27     # We assume your default Python is v 2.7.x
  $ source py27/bin/activate
  (py27) $

Now clone the sources::

  (py27) $ git clone https://github.com/ulif/ulif.gnupgtools.git
  (py27) $ cd ulif.gnupgtools

Testing
-------

Install packages for testing::

  (py27) $ python setup.py dev


If you additonally want `tox`_ tests, you might have to::

  (py27) $ pip install tox


Running tests::

  (py27) $ py.test

We also support `tox`_ to run tests for all supported Python
versions. The current list of supported Python versions is available
in `tox.ini`. Of course, for the respective tests to run you have to
have the respective Python version installed. You can, for instance,
only test with Python 2.7, if this version of Python is installed.

`tox`_ tests are triggered::

  (py27) $ tox

if tox_ is installed.


Test Coverage
-------------

Test coverage can be detected like this::

  (py27) $ py.test --cov=ulif.gnugpgtools    # for cmdline results
  (py27) $ py.test --cov=ulif.gnugpgtools --cov-report=html

The latter will generate HTML coverage reports in a subdirectory.


Documentation
-------------

We provide `Sphinx`_ docs:

  (py27) $ python setup.py docs
  (py27) $ cd doc
  (py27) $ make html

will generate the documentation in a subdirectory.


License
=======

`ulif.gnupgtools` is covered by the GPL version 3 or later.


.. testcleanup::

    from ulif.gnupgtools.testing import doctest_teardown
    doctest_teardown()


.. _Sphinx: http://sphinx-doc.org/
.. _tox: https://tox.readthedocs.org/en/latest/
