from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig
import os

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

ext = ".pyx" if USE_CYTHON else ".c"
source_files = [
    os.path.join("topocalc", "core_c", f"topo_core{ext}"),
    os.path.join("topocalc", "core_c", "hor1d.c"),
]

class build_ext(build_ext_orig):
    def finalize_options(self):
        super().finalize_options()
        import numpy
        self.include_dirs.append(numpy.get_include())

extensions = [
    Extension(
        "topocalc.core_c.topo_core",
        sources=source_files,
        # Do not specify include_dirs here; handled in build_ext
    )
]

if USE_CYTHON:
    extensions = cythonize(extensions)

setup(
    ext_modules=extensions,
    cmdclass={"build_ext": build_ext},
)