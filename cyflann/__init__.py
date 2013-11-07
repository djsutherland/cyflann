from . import index
from .index import FLANNParameters, FLANNIndex, set_distance_type

try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except ImportError:
    pass


_ldd_re = r'^\t([^\s]+) => (.*) \(0x[\da-f]+\)$'
def get_flann_lib():
    '''
    Gets the location of the flann library that users should link against.
    '''
    # Would make sense to have setup.py write out a file containing the location
    # it found (like what CMake does), but that doesn't work with Anaconda envs.
    import os
    import re
    import subprocess
    import sys

    so_name = index.__file__

    if sys.platform == 'darwin':
        out = subprocess.check_output(['otool', '-L', so_name]).split('\n')
        assert out.pop(0) == so_name + ':'
        for line in out:
            assert line[0] == '\t'
            fname = line.split(None, 1)[0]
            if 'libflann' in fname and 'libflann_cpp' not in fname:
                fname = fname.replace('@loader_path', os.path.dirname(so_name))
                return os.path.abspath(fname)
    elif sys.platform.startswith('linux'):
        out = subprocess.check_output(['ldd', so_name]).split('\n')
        for line in out:
            shortname, path = re.match(_ldd_re, line).groups()
            if 'libflann' in shortname and 'libflann_cpp' not in shortname:
                return os.path.abspath(path)
    else:
        raise OSError("get_flann_lib doesn't know how to handle this OS")
