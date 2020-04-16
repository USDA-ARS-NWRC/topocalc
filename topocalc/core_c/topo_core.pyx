# cython: embedsignature=True
"""
C implementation of some radiation functions
"""


import cython
import numpy as np
cimport numpy as np
import ctypes
# from cpython cimport bool
from libcpp cimport bool


# Numpy must be initialized. When using numpy from C or Cython you must
# _always_ do that, or you will have segfaults
np.import_array()


cdef extern from "topo_core.h":
    void hor1f(int n, double *z, int *h);
    void hor1b(int n, double *z, int *h);
    void horval(int n, double *z, double delta, int *h, double *hcos);
    void hor2d(int n, int m, double *z, double delta, bool forward, int *h, double *hcos);

@cython.boundscheck(False)
@cython.wraparound(False)
# https://github.com/cython/cython/wiki/tutorials-NumpyPointerToC
def c_hor1d(np.ndarray[double, mode="c", ndim=1] z,
           double spacing,
           bool forward,
           np.ndarray[double, mode="c", ndim=1] hcos):
    """
    Call the function hor1f in hor1f.c

    https://stackoverflow.com/questions/23435756/passing-numpy-integer-array-to-c-code

    Args:
        z: elevation array
        spacing: grid spacing
    
    Returns
        hcos: cosine angle of horizon array changed in place
    """

    cdef int n
    n = z.shape[0]

    # convert the z array to C
    cdef np.ndarray[double, mode="c", ndim=1] z_arr
    z_arr = np.ascontiguousarray(z, dtype=np.float64)

    # integer array for horizon index
    cdef np.ndarray[int, ndim=1, mode='c'] h = np.empty((n,), dtype = ctypes.c_int)

    # call the hor1f C function
    if forward:
        hor1f(n, &z_arr[0], &h[0])
    else:
        hor1b(n, &z_arr[0], &h[0])
    
    # call the horval C function
    horval(n, &z_arr[0], spacing, &h[0], &hcos[0])

@cython.boundscheck(False)
@cython.wraparound(False)
# https://github.com/cython/cython/wiki/tutorials-NumpyPointerToC
def c_hor2d(np.ndarray[double, mode="c", ndim=2] z,
           double spacing,
           bool forward,
           np.ndarray[double, mode="c", ndim=2] hcos):
    """
    Call the function hor1f in hor1f.c

    Args:
        z: elevation array
        spacing: grid spacing
    
    Returns
        hcos: cosine angle of horizon array changed in place
    """

    cdef int nrows
    cdef int ncols
    nrows = z.shape[0]
    ncols = z.shape[1]

    cdef bool fwd
    fwd = forward
    
    # convert the z array to C
    cdef np.ndarray[double, mode="c", ndim=2] z_arr
    z_arr = np.ascontiguousarray(z, dtype=np.float64)

    # integer array for horizon index
    cdef np.ndarray[int, ndim=2, mode='c'] h = np.empty((nrows,ncols), dtype = ctypes.c_int)

    # call the hor2d C function
    hor2d(nrows, ncols, &z_arr[0,0], spacing, fwd, &h[0,0], &hcos[0,0])