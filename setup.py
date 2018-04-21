# -*- coding: utf-8 -*-
"""
"""
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 1 - Planning",
]

requires = [
    "sqlalchemy",
    "flask",
]

setup(
    name="PyNuGet",
    version="0.0.1",

    description="A Python-based NuGet Server",
    long_description="TODO",

    author='Douglas Thor',
    author_email='doug.thor@gmail.com',

    url='https://github.com/dougthor42/pynuget/',
    license='MIT',

    packages=find_packages(),
    classifiers=classifiers,
    requires=requires,

    python_requires=">=3.5",
)
