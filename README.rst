This is a Cython-based interface to the
`FLANN <http://people.cs.ubc.ca/~mariusm/index.php/FLANN/FLANN>`_ library.

If you're just looking for any Python interface to FLANN, the ctypes interface
that it ships with may be better for you. I wrote this interface for
`an application <https://github.com/dougalsutherland/py-sdm/>`_
that needs to run lots of independent searches without the GIL.

The interface is currently incomplete; right now only float32 is supported, it
also has some known issues, and is probably less friendly in general than it
could be. If you want to use it, bug reports and/or pull requests are welcome.


Installation
------------

If you use the `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ Python
distribution, the easiest way to get both cyflann and FLANN is::

   conda install -c http://conda.binstar.org/dougal cyflann

Otherwise, you need to install FLANN yourself, and can then run::

   pip install cyflann

If you're using FLANN 1.8.4 or earlier (the most recent release), a problem
with its pkg-config files means that cyflann won't link properly.
This has been fixed in the development branch since April 2013, but there
hasn't been an official release since then.
To work around this problem, set the environment variable ``FLANN_DIR`` to the
root of the installation before running ``pip`` or ``setup.py``, e.g.
``/usr/local`` if the libraries are in ``/usr/local/lib/libflann.so``.

cyflann supports FLANN's OpenMP wrappers, but has not been tested with its
MPI or CUDA interfaces.
