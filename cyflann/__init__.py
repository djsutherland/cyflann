from .index import FLANNParameters, FLANNIndex, set_distance_type

try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except ImportError:
    pass
