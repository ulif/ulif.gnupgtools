ulif.gnupgtools
===============

Tools to ease use of GnuPG tasks

|build-status|_

.. .. |build-status| image:: https://travis-ci.org/ulif/ulif.gnupgtools.png?branch=master
.. .. _build-status: https://travis-ci.org/ulif/ulif.gnupgtools


Resources
=========

`ulif.gnupgtools` are hosted on

  https://github.com/ulif/ulif.gnupgtools

The documentation can be found at

  https://ulif-gnupgtools.readthedocs.org/en/latest/

.. contents::

..

  >>> from ulif.gnupgtools.testing import (
  ...   doctest_setup, doctest_teardown)
  >>> doctest_setup()

Examples
========

XXX: TBD


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

Running tests::

  (py27) $ py.test

We also support `tox` to run tests for all supported Python
versions. The current list is available in `tox.ini`. Of course, for
the respective tests to run you have to have the respective Python
version installed. You can, for instance, only test with Python 2.7,
if this version of Python is installed.


Test Coverage
-------------

Test coverage can be detected like this::

  (py27) $ py.test --cov=ulif.gnugpgtools    # for cmdline results
  (py27) $ py.test --cov=ulif.gnugpgtools --cov-report=html

The latter will generate HTML coverage reports in a subdirectory.


Documentation
-------------

We provide `Sphinx` docs:

  (py27) $ python setup.py docs
  (py27) $ cd doc
  (py27) $ make html

will generate the documentation in a subdirectory.


License
=======

`ulif.gnupgtools` is covered by the GPL version 3 or later.


..

    >>> doctest.teardown()
