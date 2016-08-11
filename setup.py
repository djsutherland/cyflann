import os
import sys
import versioneer

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins

try:
    import numpy
except ImportError as e:
    raise ImportError("cyflann requires numpy to be installed:\n{}".format(e))
    # Don't do this in the setup() requirements, because otherwise pip and
    # friends get too eager about updating numpy.

try:
    from setuptools import setup
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    from distutils.command.build_ext import build_ext

# A hack, following sklearn: set a global variable so that cyflann.__init__
# knows not to try to import compiled extensions that aren't built yet during
# the setup process.
builtins.__CYFLANN_SETUP__ = True
from cyflann.flann_info import get_flann_info
flann_info = get_flann_info()


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
    ext_modules = cythonize([
        Extension("cyflann.index", ["cyflann/index.pyx"],
                  depends=["cyflann/index.pxd", "cyflann/flann.pxd"])
    ])

for ext in ext_modules:
    ext.__dict__.update(flann_info)
    ext.include_dirs.append(numpy.get_include())


setup(
    name='cyflann',
    version=versioneer.get_version(),
    author='Dougal J. Sutherland',
    author_email='dougal@gmail.com',
    packages=['cyflann', 'cyflann.tests'],
    package_data={'cyflann': ['*.pyx', '*.pxd']},
    url='https://github.com/dougalsutherland/cyflann',
    description='A Cython-based interface to the FLANN nearest neighbors '
                'library.',
    long_description=open('README.rst').read(),
    license='BSD 3-clause',
    ext_modules=ext_modules,
    cmdclass=versioneer.get_cmdclass(),
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
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Cython",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    zip_safe=False,  # not unsafe but no point, since it's just a c ext
)
