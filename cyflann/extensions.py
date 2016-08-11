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

from .flann_info import get_flann_info


class FLANNExtension(Extension):
    def __init__(self, name, sources, **kw):
        for key, vals in get_flann_info().items():
            kw[key] = l = kw.get(key) or []
            for v in vals:
                if v not in l:
                    l.append(v)

        Extension.__init__(self, name, sources, **kw)


# Used to use this to do install_name_tool munging on OSX, but that was only
# needed for old conda and shouldn't be necessary anymore. Still here for
# backwards compatability.
class build_ext_flann(build_ext):
    pass
