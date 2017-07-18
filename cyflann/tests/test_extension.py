import os
import shutil
import sys
import tempfile

from Cython.Build import cythonize
import numpy as np
from setuptools import setup as _setup  # don't let nose run this...
from setuptools.extension import Extension

import cyflann

extension = '''
import numpy as np

cimport cython
from cyflann.flann cimport flann_index_t, FLANNParameters, \
                           flann_find_nearest_neighbors_index_float
from cyflann.index cimport FLANNIndex

@cython.boundscheck(False)
def do_test():
    np.random.seed(17)
    dim = 3
    cdef float[:, ::1] X = np.random.randn(30, dim).astype(np.float32)

    cdef FLANNIndex index = FLANNIndex(algorithm='kdtree_single')
    cdef FLANNParameters params = index.params._this

    index.build_index(X)

    n_query = 5
    k = 3
    cdef float[:, ::1] query = np.random.randn(n_query, dim).astype(np.float32)
    cdef int[:, ::1] idx_out = np.zeros((n_query, k), dtype=np.int32) - 1
    cdef float[:, ::1] dists_out = np.zeros((n_query, k), dtype=np.float32) - 1

    with nogil:
        flann_find_nearest_neighbors_index_float(
            index_id=index._this,
            testset=&query[0, 0],
            trows=n_query,
            indices=&idx_out[0, 0],
            dists=&dists_out[0, 0],
            nn=k,
            flann_params=&params)

    # check manually
    X_n = np.asarray(X)
    q_n = np.asarray(query)

    dists = ((q_n ** 2).sum(axis=1)[:, np.newaxis]
           + (X_n ** 2).sum(axis=1)[np.newaxis, :]
           - 2 * q_n.dot(X_n.T))
    inds = np.argsort(dists, axis=1)
    nn_inds = inds[:, :k]
    nn_dists = dists[np.arange(n_query)[:, np.newaxis], nn_inds]
    assert np.all(np.asarray(idx_out) == nn_inds)
    assert np.allclose(dists_out, nn_dists)
'''


def test_extension():
    tmpdir = tempfile.mkdtemp()
    old_dir = os.getcwd()
    os.chdir(tmpdir)
    print(tmpdir)
    try:
        with open('test.pyx', 'w') as f:
            f.write(extension)

        exts = cythonize(cyflann.FLANNExtension(
            'test', ['test.pyx'], include_dirs=[np.get_include()]))

        if sys.platform == 'darwin':
            import sysconfig
            s = 'MACOSX_DEPLOYMENT_TARGET'
            os.environ[s] = sysconfig.get_config_var(s)

        _setup(script_name='a_test',
               script_args=['build_ext', '--inplace'],
               ext_modules=exts)

        sys.path.insert(0, tmpdir)
        import test
        test.do_test()
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tmpdir)
        if sys.path[0] == tmpdir:
            del sys.path[0]


if __name__ == '__main__':
    test_extension()
