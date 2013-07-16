from .flann cimport FLANNParameters as Parameters, flann_index_t as index_t

cdef class FLANNParameters:
    cdef Parameters _this

cdef class FLANNIndex:
    cdef index_t _this
    cdef float[:, ::1] _data

    cdef public float speedup
    cdef public FLANNParameters params
    cdef public object _rn_gen

    cdef void _free_index(self) nogil

    cpdef _check_array(self, array, int dim=?)
    cdef _ensure_random_seed(self, kwargs)

    cdef void _nn(self, float[:, ::1] pts, float[:, ::1] qpts,
                  int num_neighbors, int[:, ::1] idx, float[:, ::1] dists) nogil
    cdef void _build_index(self, float[:, ::1] pts) nogil

    cpdef save_index(self, bytes filename)
    cdef void _load_index(self, bytes filename, float[:, ::1] pts)

    cdef void _nn_index(self, float[:, ::1] qpts, int num_neighbors,
                        int[:, ::1] idx, float[:, ::1] dists) nogil
    cdef int _nn_radius(self, float[:] query, float radius, int max_nn,
                        int[:] idx, float[:] dists) nogil

    cdef int _hierarchical_kmeans(self, float[:, ::1] pts, int num_clusters,
                                  float[:, ::1] result) nogil
