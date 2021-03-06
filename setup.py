# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os.path
from setuptools import setup, find_packages
import oyProjectManager


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#required_packages = ["pyside", "sqlalchemy", "jinja2"]
# no PySide until it is supported natively by the host applications
required_packages = ["sqlalchemy", "jinja2"]

setup(name="oyProjectManager",
      version=oyProjectManager.__version__,
      author="Erkan Ozgur Yilmaz",
      author_email="eoyilmaz@gmail.com",
      description=("A Simple Asset Management System for Animation and VFX Studios"),
      long_description=read("README"),
      keywords=["production", "asset", "management", "vfx", "animation", "maya"
                "houdini", "nuke", "xsi", "blender", "vue"],
      packages=find_packages(exclude=["tests*"]),
      platforms=["any"],
      url="http://code.google.com/p/oyprojectmanager/",
      license="http://www.opensource.org/licenses/bsd-license.php",
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "Topic :: Database",
          "Topic :: Software Development",
          "Topic :: Utilities",
          "Topic :: Office/Business :: Scheduling",
      ],
      requires=required_packages,
      install_requires=required_packages,
)
