import os
import sys

import cyflann

def test_find_sanity():
    lib = cyflann.get_flann_lib()
    assert lib.startswith('/')
    if sys.platform.startswith('linux'):
        import re
        assert re.search(r'\.so(\.\d+)*$', lib)
    elif sys.platform == 'darwin':
        assert lib.endswith('.dylib')
    assert os.path.isfile(lib)

    inc = cyflann.get_flann_include()
    assert inc.startswith('/')
    assert os.path.isdir(inc)
