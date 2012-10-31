# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
from distutils.core import setup
setup(
      name="cp2cc",
      version="0.10",
      description="My test module",
      author="Liutaihua",
      url="liutaihua.com",
      license="LGPL",
      packages= find_packages(),
      scripts=["cp2cc"],

      install_requires=[
          'requests',
      ],
)

