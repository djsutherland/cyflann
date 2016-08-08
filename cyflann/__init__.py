from . import index
from .index import FLANNParameters, FLANNIndex, set_distance_type

try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except ImportError:
    pass


################################################################################
### Helpers for consumers to find libflann

import re

_flann_lib = None
_ldd_re = re.compile(r'^\t([^\s]+)(?: => (.*))? \(0x[\da-f]+\)$')
def get_flann_lib():
    '''
    Gets the location of the flann library that users should link against.
    '''
    # Would make sense to have setup.py write out a file containing the location
    # it found (like what CMake does), but that doesn't work with Anaconda envs.
    global _flann_lib
    if _flann_lib is not None:
        return _flann_lib

    import os
    import re
    from subprocess import check_output
    import sys

    so_name = index.__file__

    if sys.platform == 'darwin':
        # this is gross. it'd be better to not have to do all this.
        out = check_output(['otool', '-L', so_name]).decode().splitlines()
        assert out.pop(0) == so_name + ':'
        for line in out:
            assert line[0] == '\t'
            fname = line.split(None, 1)[0]
            if 'libflann' in fname and 'libflann_cpp' not in fname:
                if fname.startswith('@rpath'):
                    o = check_output(['otool', '-l', so_name]).decode()
                    i = o.index('cmd LC_RPATH')
                    lines = o[i:].splitlines()
                    assert lines[0].strip() == 'cmd LC_RPATH'
                    assert re.match(r'cmdsize \d+$', lines[1].strip())
                    m = re.match(r'path (.*) \(offset \d+\)$', lines[2].strip())
                    assert m
                    fname = fname.replace('@rpath', m.group(1))

                fname = fname.replace('@loader_path', os.path.dirname(so_name))
                if '/' not in fname:
                    # relative install_names, dammit
                    # look for it in the standard places...
                    dirs = ['/usr/local/lib', '/usr/lib', '/lib']
                    if 'LIBRARY_PATH' in os.environ:
                        dirs = os.environ['LIBRARY_PATH'].split(':') + dirs

                    from distutils.unixccompiler import UnixCCompiler
                    assert fname.startswith('lib')
                    assert fname.endswith('.dylib')
                    basename = fname[len('lib'):-len('.dylib')]
                    fname = UnixCCompiler().find_library_file(dirs, basename)
                    if fname is None:
                        msg = "Can't find library file lib{}.dylib"
                        raise ValueError(msg.format(basename))
                assert fname.startswith('/')
                _flann_lib = os.path.abspath(fname)
                return _flann_lib
    elif sys.platform.startswith('linux'):
        out = check_output(['ldd', so_name]).decode().splitlines()
        for line in out:
            match = _ldd_re.match(line)
            if not match:
                import warnings
                warnings.warn("Confused by ldd output line: {}".format(line))
                continue
            shortname, path = match.groups()
            if 'libflann' in shortname and 'libflann_cpp' not in shortname:
                if path:
                    _flann_lib = os.path.abspath(path)
                    return _flann_lib
    else:
        raise OSError("get_flann_lib doesn't know how to handle this OS")

def get_flann_include():
    '''
    Gets the location of the flann headers that users should link against.
    '''
    # TODO: do this a real way....
    import os
    return os.path.abspath(os.path.join(os.path.dirname(get_flann_lib()),
                                        '../include'))

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
