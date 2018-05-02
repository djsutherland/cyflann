from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile

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

setup_code = '''
from Cython.Build import cythonize
import numpy as np
from setuptools import setup
from setuptools.extension import Extension

import cyflann

exts = cythonize(cyflann.FLANNExtension(
    'a_test', ['test.pyx'], include_dirs=[np.get_include()]))

setup(name='a_test', ext_modules=exts)
'''

def call_out(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        print(p.stdout.readline().decode('utf-8'), end='')
    print(p.stdout.read().decode('utf-8'), end='')
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, args)


def test_extension():
    tmpdir = tempfile.mkdtemp()
    old_dir = os.getcwd()
    os.chdir(tmpdir)
    print(tmpdir)
    try:
        with open('test.pyx', 'w') as f:
            f.write(extension)

        with open('setup.py', 'w') as f:
            f.write(setup_code)

        if sys.platform == 'darwin':
            import sysconfig
            s = 'MACOSX_DEPLOYMENT_TARGET'
            os.environ[s] = sysconfig.get_config_var(s)

        call_out([sys.executable, 'setup.py', 'build_ext', '--inplace'])
        call_out([sys.executable, '-c', 'import a_test; a_test.do_test()'])
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tmpdir)
        if sys.path[0] == tmpdir:
            del sys.path[0]


if __name__ == '__main__':
    test_extension()
