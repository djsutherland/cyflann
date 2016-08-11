import sys

# versioneer: get __version__ attribute
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# A bit of a hack, following numpy/sklearn: figure out whether we're being
# imported in the setup phase and so shouldn't try to import the compiled
# extensions.
try:
    __CYFLANN_SETUP__
except NameError:
    __CYFLANN_SETUP__ = False

if __CYFLANN_SETUP__:
    sys.stderr.write("Partial import of cyflann during the build process.\n")
else:
    from . import index
    from .index import FLANNParameters, FLANNIndex, set_distance_type

from . import flann_info, extensions
from .flann_info import get_flann_info
from .extensions import FLANNExtension

# A test function, if we have nose.
try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except ImportError:
    pass
