from copy import copy
import os
import tempfile

cimport cython

import numpy as np
cimport numpy as np

cimport flann
from flann cimport (flann_index_t as index_t,
                    flann_algorithm_t as algorithm_t,
                    flann_centers_init_t as centers_init_t,
                    flann_distance_t as distance_t,
                    flann_log_level_t as log_level_t,
                    FLANNParameters as Parameters,
                    DEFAULT_FLANN_PARAMETERS as DEFAULT_PARAMETERS,
                    flann_build_index_float as build_index_float)

################################################################################
### Enum conversions

str_to_algorithm_t = {
    'linear': flann.FLANN_INDEX_LINEAR,
    'kdtree': flann.FLANN_INDEX_KDTREE,
    'kmeans': flann.FLANN_INDEX_KMEANS,
    'composite': flann.FLANN_INDEX_COMPOSITE,
    'kdtree_single': flann.FLANN_INDEX_KDTREE_SINGLE,
    'hierarchical': flann.FLANN_INDEX_HIERARCHICAL,
    'lsh': flann.FLANN_INDEX_LSH,
    'saved': flann.FLANN_INDEX_SAVED,
    'autotuned': flann.FLANN_INDEX_AUTOTUNED,
}
algorithm_t_to_str = {v: k for k, v in str_to_algorithm_t.iteritems()}

str_to_centers_init_t = {
    'random': flann.FLANN_CENTERS_RANDOM,
    'gonzales': flann.FLANN_CENTERS_GONZALES,
    'kmeanspp': flann.FLANN_CENTERS_KMEANSPP,
}
centers_init_t_to_str = {v: k for k, v in str_to_centers_init_t.iteritems()}

str_to_log_level_t = {
    'none': flann.FLANN_LOG_NONE,
    'fatal': flann.FLANN_LOG_FATAL,
    'error': flann.FLANN_LOG_ERROR,
    'warn': flann.FLANN_LOG_WARN,
    'info': flann.FLANN_LOG_INFO,
    'debug': flann.FLANN_LOG_DEBUG,
}
log_level_t_to_str = {v: k for k, v in str_to_log_level_t.iteritems()}

str_to_distance_t = {
    'euclidean': flann.FLANN_DIST_EUCLIDEAN,
    'l2': flann.FLANN_DIST_L2,
    'manhattan': flann.FLANN_DIST_MANHATTAN,
    'l1': flann.FLANN_DIST_L1,
    'minkowski': flann.FLANN_DIST_MINKOWSKI,
    'max_dist': flann.FLANN_DIST_MAX,
    'hik': flann.FLANN_DIST_HIST_INTERSECT,
    'hellinger': flann.FLANN_DIST_HELLINGER,
    'chi_square': flann.FLANN_DIST_CHI_SQUARE,
    'kullback_leibler': flann.FLANN_DIST_KULLBACK_LEIBLER,
    'hamming': flann.FLANN_DIST_HAMMING,
    'hamming_lut': flann.FLANN_DIST_HAMMING_LUT,
    'hamming_popcnt': flann.FLANN_DIST_HAMMING_POPCNT,
    'l2_simple': flann.FLANN_DIST_L2_SIMPLE,
}
distance_t_to_str = {
    flann.FLANN_DIST_EUCLIDEAN: 'euclidean',
    flann.FLANN_DIST_MANHATTAN: 'manhattan',
    flann.FLANN_DIST_MINKOWSKI: 'minkowski',
    flann.FLANN_DIST_MAX: 'max_dist',
    flann.FLANN_DIST_HIST_INTERSECT: 'hik',
    flann.FLANN_DIST_HELLINGER: 'hellinger',
    flann.FLANN_DIST_CHI_SQUARE: 'chi_square',
    flann.FLANN_DIST_KULLBACK_LEIBLER: 'kullback_leibler',
    flann.FLANN_DIST_HAMMING: 'hamming',
    flann.FLANN_DIST_HAMMING_LUT: 'hamming_lut',
    flann.FLANN_DIST_HAMMING_POPCNT: 'hamming_popcnt',
    flann.FLANN_DIST_L2_SIMPLE: 'l2_simple',
}

def set_distance_type(str distance_type, int order = 0):
    cdef distance_t dist = str_to_distance_t[distance_type]
    flann.flann_set_distance_type(dist, order)


################################################################################
### Wrapping parameters struct

cdef class FLANNParameters:
    # attributes in the pxd: _this
    def __cinit__(self):
        self._this = DEFAULT_PARAMETERS

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __getitem__(self, k):
        try:
            return getattr(self, k)
        except AttributeError as e:
            raise KeyError(*e.args)

    def __setitem__(self, k, v):
        try:
            setattr(self, k, v)
        except AttributeError as e:
            raise KeyError(*e.args)

    def update(self, dict={}, **kwargs):
        for k, v in dict.iteritems():
            setattr(self, k, v)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def as_dict(self):
        cdef dict d = dict(self._this)
        d['algorithm'] = self.algorithm
        d['centers_init'] = self.centers_init
        d['log_level'] = self.log_level
        return d

    def __repr__(self):
        return "<FLANNParameters {}>".format(self.as_dict())

    property algorithm:
        # the algorithm to use
        def __get__(self):
            return algorithm_t_to_str[self._this.algorithm]
        def __set__(self, str algorithm):
            cdef algorithm_t algo = str_to_algorithm_t[algorithm]
            self._this.algorithm = algo

    # search time parameters
    property checks:  # TODO: also support unlimited, autotuned
        # how many leaves (features) to check in one search
        def __get__(self): return self._this.checks
        def __set__(self, int checks): self._this.checks = checks
    property eps:
        # eps parameter for eps-knn search
        def __get__(self): return self._this.eps
        def __set__(self, float eps): self._this.eps = eps
    property sorted:
        # indicates if results returned by radius search should be sorted or not
        def __get__(self): return bool(self._this.sorted)
        def __set__(self, bint sorted):
            self._this.sorted = sorted
    property max_neighbors:
        # limits the max number of neighbors should be returned by radius search
        def __get__(self): return self._this.max_neighbors
        def __set__(self, int max_neighbors):
            self._this.max_neighbors = max_neighbors
    property cores:
        # number of parallel cores to use for searching
        def __get__(self): return self._this.cores
        def __set__(self, int cores): self._this.cores = cores

    # KD tree params
    property trees:
        # number of randomized trees to use (for kdtree)
        def __get__(self): return self._this.trees
        def __set__(self, int trees): self._this.trees = trees
    property leaf_max_size:
        def __get__(self): return self._this.leaf_max_size
        def __set__(self, int leaf_max_size):
            self._this.leaf_max_size = leaf_max_size

    # kmeans index params
    property branching:
        # branching factor (for kmeans tree)
        def __get__(self): return self._this.branching
        def __set__(self, int branching): self._this.branching = branching
    property iterations:
        # max iterations to perform in one kmeans clustering (kmeans tree)
        def __get__(self): return self._this.iterations
        def __set__(self, int iterations): self._this.iterations = iterations
    property centers_init:
        # algorithm used for picking the initial cluster centers for kmeans tree
        def __get__(self):
            return centers_init_t_to_str[self._this.centers_init]
        def __set__(self, str centers_init):
            cdef centers_init_t init = str_to_centers_init_t[centers_init]
            self._this.centers_init = init
    property cb_index:
        # cluster boundary index. Used when searching the kmeans tree
        def __get__(self): return self._this.cb_index
        def __set__(self, float cb_index): self._this.cb_index = cb_index

    # autotuned index parameters
    property target_precision:
        # precision desired (used for autotuning, -1 otherwise) */
        def __get__(self): return self._this.target_precision
        def __set__(self, float target_precision):
            self._this.target_precision = target_precision
    property build_weight:
        # build tree time weighting factor
        def __get__(self): return self._this.build_weight
        def __set__(self, float build_weight):
            self._this.build_weight = build_weight
    property memory_weight:
        # index memory weigthing factor
        def __get__(self): return self._this.memory_weight
        def __set__(self, float memory_weight):
            self._this.memory_weight = memory_weight
    property sample_fraction:
        # what fraction of the dataset to use for autotuning
        def __get__(self): return self._this.sample_fraction
        def __set__(self, float sample_fraction):
            self._this.sample_fraction = sample_fraction

    # LSH parameters
    property table_number_:
        # The number of hash tables to use
        def __get__(self): return self._this.table_number_
        def __set__(self, int table_number_):
            self._this.table_number_ = table_number_
    property key_size_:
        # The length of the key in the hash tables
        def __get__(self): return self._this.key_size_
        def __set__(self, int key_size_): self._this.key_size_ = key_size_
    property multi_probe_level_:
        # Number of levels to use in multi-probe LSH, 0 for standard LSH
        def __get__(self): return self._this.multi_probe_level_
        def __set__(self, int multi_probe_level_):
            self._this.multi_probe_level_ = multi_probe_level_

    # other parameters
    property log_level:
        # determines the verbosity of each flann function
        def __get__(self): return log_level_t_to_str[self._this.log_level]
        def __set__(self, str log_level):
            cdef log_level_t level = str_to_log_level_t[log_level]
            self._this.log_level = level
    property random_seed:
        # random seed to use
        def __get__(self): return self._this.random_seed
        def __set__(self, long random_seed):
            self._this.random_seed = random_seed


################################################################################
### Wrapping index class

# TODO: template across different types
cdef class FLANNIndex:
    # attributes in the pxd: _this, _data, speedup, params

    def __cinit__(self):
        self._this = NULL
        # TODO: _data?
        self.speedup = -1
        self.params = FLANNParameters()

    def __init__(self, **kwargs):
        self.params.update(**kwargs)

    def free_index(self):
        self._free_index()

    cdef void _free_index(self) nogil:
        flann.flann_free_index_float(self._this, &self.params._this)
        self._this = NULL
        with gil:  # TODO: how to handle this more appropriately?
            self._data = np.empty((0, 0), dtype=np.float32)

    def __dealloc__(self):
        if self._this is not NULL:
            self._free_index()

    property data:
        def __get__(self):
            try:
                return np.asarray(self._data)
            except AttributeError:
                return None

    ############################################################################
    ### general helpers

    cdef _ensure_random_seed(self, kwargs):
        if 'random_seed' not in kwargs:
            kwargs['random_seed'] = np.random.randint(2 ** 30)

    cpdef _check_array(self, array, int dim=2):
        array = np.require(array,
                    requirements=['C_CONTIGUOUS', 'ALIGNED'],
                    dtype=np.float32)
        if dim == 2 and array.ndim == 1:
            array = array.reshape(1, array.size)
        if array.ndim != dim:
            raise ValueError("expected a {}d array".format(dim))
        return array

    ############################################################################
    ### I/O

    cpdef save_index(self, bytes filename):
        "Saves the index to a file on disk."
        if self._this is NULL:
            raise ValueError("index doesn't exist, can't save it")
        flann.flann_save_index_float(self._this, filename)


    def load_index(self, bytes filename, pts):
        "Loads an index previously saved to disk."
        cdef float[:, ::1] the_pts = self._check_array(pts)
        self._load_index(filename, the_pts)

    cdef void _load_index(self, bytes filename, float[:, ::1] pts):
        self._free_index()
        self._this = flann.flann_load_index_float(
            filename, &pts[0, 0], pts.shape[0], pts.shape[1])
        self._data = pts

    def __reduce__(self):
        fname = tempfile.NamedTemporaryFile(delete=False).name
        try:
            self.save_index(fname.encode())
            with open(fname, 'rb') as f:
                return FLANNIndex, (), (f.read(), self.data)
        finally:
            os.remove(fname)

    def __setstate__(self, state):
        idx, data = state
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            f.write(idx)
        try:
            self.load_index(fname.encode(), data)
        finally:
            os.remove(fname)

    ############################################################################
    ### Main NN search functions

    def nn(self, pts, qpts, int num_neighbors = 1, **kwargs):
        '''
        Finds the num_neighbors nearest points to each point in pts.

        Returns a pair:
            - a (num_qpts, num_neighbors) integer array of indices
            - a (num_qpts, num_neighbors) float array of distances
        If num_neighbors == 1, the results are 1-dimensional.
        '''
        cdef float[:, ::1] the_pts = self._check_array(pts)
        cdef float[:, ::1] the_qpts = self._check_array(qpts)

        cdef int npts = the_pts.shape[0], dim = the_pts.shape[1]
        cdef int nqpts = the_qpts.shape[0], qdim = the_qpts.shape[1]
        if qdim != dim:
            raise TypeError("data is dim {}, query is dim {}".format(dim, qdim))

        if num_neighbors > npts:
            raise ValueError("asking for {} neighbors from a set of size {}"
                             .format(num_neighbors, npts))

        # TODO: should this set the random seed? pyflann doesn't, but seems
        #       like it should be the same as build_index()...
        self.params.update(**kwargs)

        cdef tuple shape = (nqpts, num_neighbors)
        cdef np.ndarray idx = np.empty(shape, dtype=np.int32)
        cdef np.ndarray dists = np.empty(shape, dtype=np.float32)

        self._nn(the_pts, the_qpts, num_neighbors, idx, dists)
        if num_neighbors == 1:
            return idx[:, 0], dists[:, 0]
        else:
            return idx, dists

    @cython.boundscheck(False)
    cdef void _nn(self, float[:, ::1] pts, float[:, ::1] qpts,
                  int num_neighbors,
                  int[:, ::1] idx, float[:, ::1] dists) nogil:
        flann.flann_find_nearest_neighbors_float(
            dataset=&pts[0, 0], rows=pts.shape[0], cols=pts.shape[1],
            testset=&qpts[0, 0], trows=qpts.shape[0],
            indices=&idx[0, 0], dists=&dists[0, 0],
            nn=num_neighbors, flann_params=&self.params._this)


    def build_index(self, pts, **kwargs):
        '''
        This builds and stores an index to be used for future searches with
        nn_index(), overriding any previous index. Use multiple instances of
        this class to work with multiple stored indices.

        pts should be a 2d, row-instance numpy array. It will be converted to
        float32 before being used.
        '''
        # TODO: handle random seed
        cdef float[:, ::1] the_pts = self._check_array(pts)
        self._ensure_random_seed(kwargs)
        self.params.update(**kwargs)
        self._build_index(the_pts)

    @cython.boundscheck(False)
    cdef void _build_index(self, float[:, ::1] pts) nogil:
        if self._this is not NULL:
            self._free_index()

        self.speedup = -1
        self._this = flann.flann_build_index_float(
            &pts[0, 0], pts.shape[0], pts.shape[1],
            &self.speedup, &self.params._this)
        self._data = pts


    def nn_index(self, qpts, int num_neighbors = 1, **kwargs):
        '''
        Returns the num_neighbors nearest points to each point in qpts.
        Searches in the index previously built by build_index().
        '''
        if self._this is NULL:
            raise ValueError("need to build index first")

        cdef float[:, ::1] the_qpts = self._check_array(qpts)

        cdef int npts = self._data.shape[0], dim = self._data.shape[1]
        cdef int nqpts = the_qpts.shape[0], qdim = the_qpts.shape[1]
        if qdim != dim:
            raise TypeError("data is dim {}, query is dim {}".format(dim, qdim))

        if num_neighbors > npts:
            raise ValueError("asking for {} neighbors from a set of size {}"
                             .format(num_neighbors, npts))

        self.params.update(**kwargs)

        cdef tuple shape = (nqpts, num_neighbors)
        cdef np.ndarray idx = np.empty(shape, dtype=np.int32)
        cdef np.ndarray dists = np.empty(shape, dtype=np.float32)

        self._nn_index(the_qpts, num_neighbors, idx, dists)
        if num_neighbors == 1:
            return idx[:, 0], dists[:, 0]
        else:
            return idx, dists

    @cython.boundscheck(False)
    cdef void _nn_index(self, float[:, ::1] qpts, int num_neighbors,
                        int[:, ::1] idx, float[:, ::1] dists) nogil:
        flann.flann_find_nearest_neighbors_index_float(
            self._this, testset=&qpts[0, 0], trows=qpts.shape[0],
            indices=&idx[0, 0], dists=&dists[0, 0], nn=num_neighbors,
            flann_params=&self.params._this)


    def nn_radius(self, query, float radius, int max_nn=-1, **kwargs):
        """
        Finds points within a given radius of the query point, based on the
        index from build_index().

        Note that in the default euclidean metric, radius should be the
        *squared* euclidean distance.

        Finds up to min(max_nn, params.max_neighbors) points. (If either value
        is negative, it's interpreted as meaning all possible points.)

        params.sorted indicates whether the results should be sorted.
        """
        if self._this is NULL:
            raise ValueError("need to build index first")

        cdef float[:] the_query = self._check_array(query, dim=1)

        cdef int npts = self._data.shape[0], dim = self._data.shape[1]
        cdef int qdim = the_query.shape[0]
        if qdim != dim:
            raise TypeError("data is dim {}, query is dim {}".format(dim, qdim))

        self.params.update(**kwargs)

        if max_nn < 0:
            max_nn = npts

        cdef np.ndarray idx = np.empty(max_nn, dtype=np.int32)
        cdef np.ndarray dists = np.empty(max_nn, dtype=np.float32)

        cdef int nn = self._nn_radius(the_query, radius, max_nn, idx, dists)
        return idx[:nn], dists[:nn]

    @cython.boundscheck(False)
    cdef int _nn_radius(self, float[:] query, float radius, int max_nn,
                        int[:] idx, float[:] dists) nogil:
        return flann.flann_radius_search(
            self._this, query=&query[0], indices=&idx[0], dists=&dists[0],
            max_nn=max_nn, radius=radius, flann_params=&self.params._this)


    ############################################################################
    ### Clustering functions

    def kmeans(self, pts, int num_clusters, int max_iterations = -1, **kwargs):
        """
        Runs k-means on pts with num_clusters centroids.
        Returns a numpy array of shape (num_clusters x dim).

        If max_iterations is not -1, the algorithm terminates after the given
        number of iterations regardless of convergence. The default is to run
        until convergence.
        """

        if num_clusters < 1:
            raise ValueError("num_clusters should be a positive integer")
        elif num_clusters == 1:
            return np.mean(pts, axis=0).reshape(1, pts.shape[1])

        return self.hierarchical_kmeans(
            pts=pts, branch_size=int(num_clusters), num_branches=1,
            max_iterations=max_iterations, **kwargs)

    def hierarchical_kmeans(self, pts, int branch_size, int num_branches,
                            int max_iterations = -1, **kwargs):
        """
        Clusters the data by using multiple runs of kmeans to
        recursively partition the dataset. The number of resulting
        clusters is given by (branch_size-1)*num_branches+1.

        This method can be significantly faster when the number of
        desired clusters is quite large (e.g. a hundred or more).
        Higher branch sizes are slower but may give better results.
        """

        if branch_size < 2:
            raise ValueError("branch_size must be an integer >= 2")
        if num_branches < 1:
            raise ValueError("num_branches must be an integer >= 1")

        cdef float[:, ::1] the_pts = self._check_array(pts)
        cdef int npts = the_pts.shape[0], dim = the_pts.shape[1]
        cdef int num_clusters = (branch_size - 1) * num_branches + 1

        self._ensure_random_seed(kwargs)
        self.params.update(**kwargs)
        self.params.iterations = max_iterations
        self.params.algorithm = 'kmeans'
        self.params.branching = branch_size

        cdef np.ndarray result = np.empty((num_clusters, dim), dtype=np.float32)

        cdef int real_numclusters = self._hierarchical_kmeans(
            the_pts, num_clusters, result)

        if real_numclusters <= 0:
            raise ValueError("Error occurred during clustering procedure.")
        return result

    @cython.boundscheck(False)
    cdef int _hierarchical_kmeans(self, float[:, ::1] pts, int num_clusters,
                                  float[:, ::1] result) nogil:
        return flann.flann_compute_cluster_centers_float(
            dataset=&pts[0,0], rows=pts.shape[0], cols=pts.shape[1],
            clusters=num_clusters, result=&result[0, 0],
            flann_params=&self.params._this)
