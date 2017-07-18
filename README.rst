|Travis|_

.. |Travis| image:: https://api.travis-ci.org/dougalsutherland/cyflann.svg?branch=master
.. _Travis: https://travis-ci.org/dougalsutherland/cyflann

cyflann
=======

This is a Cython-based interface to the
`FLANN <http://people.cs.ubc.ca/~mariusm/index.php/FLANN/FLANN>`_ library.

If you're just looking for any Python interface to FLANN, the ctypes interface
that it ships with may be better for you. I wrote this interface for
`an application <https://github.com/dougalsutherland/py-sdm/>`_
that needs to run lots of independent searches without the GIL.

The interface is currently incomplete; right now only float32 is supported, it
also has some known issues, and is probably less friendly in general than it
could be. If you want to use it, bug reports and/or pull requests are welcome.

cyflann is only tested with FLANNs since 1.8.4.
cyflann supports FLANN's OpenMP wrappers, but has not been tested with its
MPI or CUDA interfaces.

It should work on Windows, but I haven't been able to get FLANN built there to test. If you care about that, consider helping to get a Windows build working in conda-forge (`PR <https://github.com/conda-forge/flann-feedstock/pull/1>`_).


Installation
------------

If you use the `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ Python
distribution, the easiest way to get both cyflann and FLANN is::

   conda install -c dougal -c conda-forge cyflann

Otherwise, you need to install FLANN yourself (see below), and can then run::

   pip install cyflann

**NOTE:** If you're using FLANN 1.8.4 or earlier, a problem
with its pkg-config files means that cyflann won't link properly.
This has been fixed in the development branch since April 2013, but the
1.9.1 release isn't yet widely packaged.

To work around this problem, set the environment variable ``FLANN_DIR`` to the
root of the installation before running ``pip`` or ``setup.py``, e.g.
``/usr/local`` if the libraries are in ``/usr/local/lib/libflann.so``.
If you're using ``sudo``, remember that it doesn't necessarily propagate 
environment variables by default;
``sudo FLANN_DIR=/wherever pip install cyflann`` will work.


Installing FLANN
----------------

**Anaconda:** ``conda install -c conda-forge flann`` (included as a requirement by the cyflann package).

**OSX:** using `Homebrew <http://brew.sh>`_, ``brew install homebrew/science/flann``; this gives you 1.9.1, but if ``pkg-config`` doesn't work for you for some reason, it's ``FLANN_DIR=$(brew --prefix)``.

**Ubuntu:** ``apt-get install libflann1 flann-dev``; set ``FLANN_DIR=/usr``.

**Fedora:** ``yum install flann flann-devel``; set ``FLANN_DIR=/usr``.

**CentOS:** 
`EPEL <https://fedoraproject.org/wiki/EPEL>`_ has flann packages,
but they're old and not tested with cyflann. Compile from source.

**Arch:**
Install the `AUR flann package <https://aur.archlinux.org/packages/flann/>`_;
cyflann wants ``FLANN_DIR=/usr``.

**From source:**
Download `the release source <https://github.com/mariusmuja/flann/releases>`_,
and follow the `user manual <http://www.cs.ubc.ca/research/flann/uploads/FLANN/flann_manual-1.8.4.pdf>`_ to install.
If you're installing 1.9.1 and have ``pkg-config`` available,
you shouldn't need to set ``FLANN_DIR``,
but if not set it to whatever you set ``CMAKE_INSTALL_PREFIX`` to
(``/usr/local`` by default).
