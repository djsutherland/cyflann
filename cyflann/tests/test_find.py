import os

import cyflann

def test_find_sanity():
    lib = cyflann.get_flann_lib()
    assert lib.startswith('/')
    assert lib.endswith('.so') or lib.endswith('.dylib') or lib.endswith('.dll')
    assert os.path.isfile(lib)

    inc = cyflann.get_flann_include()
    assert inc.startswith('/')
    assert os.path.isdir(lib)
