try:
    import numpy
except ImportError:
    raise ImportError("cyflann requires numpy to be installed")
    # Don't do this in the setup() requirements, because otherwise pip and
    # friends get too eager about updating numpy.

try:
    from setuptools import setup
    from setuptools.extension import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    import os
    src_path = os.path.join(os.path.dirname(__file__), 'cyflann')
    if not os.path.exists(os.path.join(src_path, 'index.c')):
        msg = "index extension needs to be compiled but cython isn't available"
        raise ImportError(msg)
else:
    cythonize("cyflann/index.pyx", "cyflann/flann.pdx")
ext_modules = [
    Extension("cyflann.index", ["cyflann/index.c"], extra_link_args=['-lflann'])
]

setup(
    name='cyflann',
    version='0.1.2',
    author='Dougal J. Sutherland',
    author_email='dougal@gmail.com',
    packages=['cyflann'],
    package_data={'cyflann': ['*.pxd']},
    url='https://github.com/dougalsutherland/cyflann',
    description='A Cython-based interface to the FLANN nearest neighbors library.',
    long_description=open('README.rst').read(),
    license='LICENSE.txt',
    install_requires=[],
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
)
