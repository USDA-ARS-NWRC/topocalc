#!/usr/bin/env python

import os
import sys
from subprocess import check_output

import numpy
from setuptools import Extension, find_packages, setup

from Cython.Distutils import build_ext

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = [ ]

test_requirements = [ ]

# force the compiler to use gcc
os.environ["CC"] = "gcc"

cmdclass = {'build_ext': build_ext}
ext_modules = []

# topocalc core c functions
loc = 'viewf/core_c'  # location of the folder
mname = os.path.join(loc, 'topo_core')
mname = mname.replace('/', '.')
ext_modules += [
    Extension(mname,
              sources=[os.path.join(loc, val) for val in [
                  "topo_core.pyx",
                  "hor1d.c",
              ]],
              include_dirs=[numpy.get_include()],
              extra_compile_args=['-fopenmp', '-O3'],
              extra_link_args=['-fopenmp', '-O3']
              ),
]

setup(
    author="Scott Havens",
    author_email='scott.havens@ars.usda.gov',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Sky view and terrain configuration factors",
    entry_points={
        'console_scripts': [
            'viewf=viewf.cli:main',
        ],
    },
    install_requires=requirements,
    license="CC0 1.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='viewf',
    name='viewf',
    packages=find_packages(include=['viewf', 'viewf.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    url='https://github.com/scotthavens/viewf',
    version='0.1.0',
    zip_safe=False,
)
