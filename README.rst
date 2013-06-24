This is a Cython-based interface to the
`FLANN <http://people.cs.ubc.ca/~mariusm/index.php/FLANN/FLANN>`_ library.

If you're just looking for any Python interface to FLANN, the ctypes interface
that it ships with is probably better for you. I wrote this interface for
`an application <https://github.com/dougalsutherland/py-sdm/>`_
that needs to run lots of independent searches without the GIL.

The interface is currently incomplete; it only does what I needed to use, so
some methods are unimplemented and right now only float32 is supported. It
also has some known issues and is probably less friendly in general than it
could be. If you want to use it, bug reports and/or pull requests are welcome.
