from setuptools import setup
from Cython.Build import cythonize
import glob
from distutils.extension import Extension

py_files = [file for file in glob.glob('recognize/*.py') if not file.endswith("__init__.py")]

ext_modules = cythonize(py_files, build_dir="build")

setup(
    name="recognize",
    version="1.0",
    author="lijiang",
    author_email="2379376998@qq.com",
    ext_modules=cythonize(ext_modules),
    description="In preparation for the Beijing Games, the date is January 4, 2024",
)