#!/usr/bin/env python

import os

import numpy
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext as _build_ext

# Test if compiling with cython or using the C source
try:
    from Cython.Distutils import build_ext as _build_ext
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True

print('Using Cython {}'.format(USE_CYTHON))
ext = '.pyx' if USE_CYTHON else '.c'


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ['setuptools_scm']

test_requirements = []

# Give user option to specify their local compiler name
if "CC" not in os.environ:
    os.environ["CC"] = "gcc"

cmdclass = {'build_ext': build_ext}
ext_modules = []

# topocalc core c functions
loc = 'topocalc/core_c'  # location of the folder
mname = os.path.join(loc, 'topo_core')
mname = mname.replace('/', '.')
ext_modules += [
    Extension(mname,
              sources=[os.path.join(loc, val) for val in [
                  "topo_core.pyx",
                  "hor1d.c",
              ]],
              include_dirs=[numpy.get_include()],
              ),
]

setup(
    author="USDA ARS NWRC",
    author_email='snow@ars.usda.gov',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    description="Topo calculations like gradient and sky view",
    entry_points={
        'console_scripts': [
            'topocalc=topocalc.cli:main',
        ],
    },
    install_requires=requirements,
    license="CC0 1.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='topocalc',
    name='topocalc',
    packages=find_packages(include=['topocalc', 'topocalc.*']),
    setup_requires=setup_requirements,
    test_suite='topocalc.tests',
    tests_require=test_requirements,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    url='https://github.com/USDA-ARS-NWRC/topocalc',
    use_scm_version={
        "local_scheme": "no-local-version"
    },
    zip_safe=False,
)
