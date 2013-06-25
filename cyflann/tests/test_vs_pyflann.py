from functools import partial
import numpy as np
import pyflann
import cyflann

def check_match(py_ids, py_dists, cy_ids, cy_dists):
    assert np.all(py_ids == cy_ids), \
           "{}/{} different".format(np.sum(py_ids != cy_ids), py_ids.size)
    assert np.allclose(py_dists, cy_dists, atol=1e-5, rtol=1e-4), \
           "max distance {}".format(np.abs(py_dists - cy_dists).max())

def test_normal():
    for dim in [1, 4, 10]:
        for k in [1, 2, 5]:
            data = np.random.normal(scale=100, size=(1000, dim))
            query = np.random.normal(scale=100, size=(100, dim))

            py = pyflann.FLANN(algorithm='kdtree_single')
            cy = cyflann.FLANNIndex(algorithm='kdtree_single')

            py.build_index(data)
            cy.build_index(data)

            py_ids, py_dists = py.nn_index(query, k)
            cy_ids, cy_dists = cy.nn_index(query, k)

            f = partial(check_match, py_ids, py_dists, cy_ids, cy_dists)
            f.description = 'normal vs pyflann - dim {} - k {}'.format(dim, k)
            yield f
