import errno
from functools import partial
import os
import subprocess
import sys

try:
    import numpy
except ImportError as e:
    raise ImportError("cyflann requires numpy to be installed:\n{}".format(e))
    # Don't do this in the setup() requirements, because otherwise pip and
    # friends get too eager about updating numpy.

try:
    from setuptools import setup
    from setuptools.extension import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

################################################################################
# The following chunk of code for querying pkg-config is loosely based on code
# from the cffi package, which is licensed as follows:
#
#    The MIT License
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or
#    sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.

def _ask_pkg_config(lib, option, result_prefix='', sysroot=False, default=None):
    pkg_config = os.environ.get('PKG_CONFIG', 'pkg-config')
    try:
        output = subprocess.check_output([pkg_config, option, lib])
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    except subprocess.CalledProcessError:
        pass
    else:
        res = output.decode().strip().split()

        # '-I/usr/...' -> '/usr/...'
        for x in res:
            assert x.startswith(result_prefix)
        res = [x[len(result_prefix):] for x in res]

        if sysroot:
            sysroot = os.environ.get('PKG_CONFIG_SYSROOT_DIR', '')
        if sysroot:
            # old versions of pkg-config don't support this env var,
            # so here we emulate its effect if needed
            res = [path if path.startswith(sysroot) else sysroot + path
                   for path in res]

        return res
    return [] if default is None else default


def get_pkg_info(name):
    ask = partial(_ask_pkg_config, name)
    return {
        'libraries': ask('--libs-only-l', '-l', default=[name]),
        'include_dirs': ask('--cflags-only-I', '-I', sysroot=True),
        'library_dirs': ask('--libs-only-L', '-L', sysroot=True),
        'extra_compile_args': ask('--cflags-only-other'),
        'extra_link_args': ask('--libs-only-other'),
        'runtime_library_dirs': ask('--variable=libdir'),
    }

if os.environ.get('FLANN_DIR', False):
    pre = partial(os.path.join, os.environ['FLANN_DIR'])
    lib_dirs = [pre('lib')]
    if os.path.isdir(pre('lib64')) and sys.maxsize > 2**32:
        lib_dirs.append(pre('lib64'))

    flann_info = {
        'libraries': ['flann', 'flann_cpp'],
        'include_dirs': [pre('include')],
        'library_dirs': lib_dirs,
        'extra_compile_args': [],
        'extra_link_args': [],
        'runtime_library_dirs': lib_dirs,
    }
else:
    flann_info = get_pkg_info('flann')

if sys.platform == 'darwin':
    # OSX rpath support is weird and stupid; just use an absolute path instead
    ld = flann_info['library_dirs']
    rld = flann_info['runtime_library_dirs']

    if len(ld) == 1 and rld == ld:
        del flann_info['runtime_library_dirs'], flann_info['library_dirs']
        flann_info['libraries'] = [
            os.path.join(ld[0], lib) for lib in flann_info['libraries']]
    elif not ld and not rld:
        pass
    else:
        import warnings
        msg = "Something unexpected is going on here. Good luck!"
        warnings.warn(msg)


################################################################################

try:
    from Cython.Build import cythonize
except ImportError:
    src_path = os.path.join(os.path.dirname(__file__), 'cyflann')
    if not os.path.exists(os.path.join(src_path, 'index.c')):
        msg = "index extension needs to be compiled but cython isn't available"
        raise ImportError(msg)
    ext_modules = [
        Extension("cyflann.index", ["cyflann/index.c"]),
    ]
else:
    ext_modules = cythonize("cyflann/*.pyx", "cyflann/*.pdx")

for ext in ext_modules:
    ext.__dict__.update(flann_info)


setup(
    name='cyflann',
    version='0.1.19',
    author='Dougal J. Sutherland',
    author_email='dougal@gmail.com',
    packages=['cyflann', 'cyflann.tests'],
    package_data={'cyflann': ['*.pyx', '*.pxd']},
    url='https://github.com/dougalsutherland/cyflann',
    description='A Cython-based interface to the FLANN nearest neighbors '
                'library.',
    long_description=open('README.rst').read(),
    license='BSD 3-clause',
    include_dirs=[numpy.get_include()],
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Cython",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    zip_safe=False,  # not unsafe but no point, since it's just a c ext
)
