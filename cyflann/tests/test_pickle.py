try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy as np
import sys

import cyflann
import pytest


@pytest.mark.skipif(sys.version_info < (3,) and sys.platform == 'win32',
                    reason="pickling is broken on win32 with python 2")
def test_pickle():
    data = np.random.normal(scale=100, size=(1000, 3))
    query = np.random.normal(scale=100, size=(100, 3))

    idx = cyflann.FLANNIndex(algorithm='kdtree_single')
    idx.build_index(data)
    res_i, res_dists = idx.nn_index(query, 2)

    s = pickle.dumps(idx)
    del idx
    idx = pickle.loads(s)

    res_i2, res_dists2 = idx.nn_index(query, 2)
    assert np.all(res_i == res_i2)
