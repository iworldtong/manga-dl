#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: muketong 
@file: setup.py 
@time: 2020-08-13

打包配置文件

"""
import os
import sys
import setuptools

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("rm -rf dist")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "manga_dl", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    # test_suite="tests",
    entry_points={"console_scripts": ["manga-dl = manga_dl.__main__:main"]},
    install_requires=["requests", "click", "pycryptodome", "prettytable", "tenacity", "pyaes", "watchdog", "PyExecJS"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
)
