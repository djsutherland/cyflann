'''
Helpers for consumers to compile FLANN extensions.
'''
import os
import subprocess
import sys

try:
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.extension import Extension
    from distutils.command.build_ext import build_ext

from . import get_flann_lib, get_flann_include


class FLANNExtension(Extension):
    def __init__(self, name, sources, **kw):
        def add_to(arg, val):
            kw[arg] = l = kw.get(arg) or []
            for v in val:
                if v not in l:
                    l.append(v)

        libdir = os.path.dirname(get_flann_lib())

        add_to('libraries', ['flann', 'flann_cpp'])
        add_to('include_dirs', [get_flann_include()])
        add_to('library_dirs', [libdir])
        add_to('runtime_library_dirs', [libdir])

        Extension.__init__(self, name, sources, **kw)


class build_ext_flann(build_ext):
    def build_extension(self, ext):
        build_ext.build_extension(self, ext)
        self._process_flann(ext)

    def _process_flann(self, ext):
        if isinstance(ext, FLANNExtension) and sys.platform == 'darwin':
            # if flann is installed with a bad install_name (e.g. conda)
            ext_name = self.get_ext_fullpath(ext.name)
            libdir, libname = os.path.split(get_flann_lib())
            for lib in [libname, 'libflann.dylib', 'libflann_cpp.dylib']:
                args = ['/usr/bin/install_name_tool',
                        '-change', lib, os.path.join(libdir, lib), ext_name]
                print(' '.join(args))
                subprocess.check_call(args)
