# -*- coding: utf-8 -*-
"""
"""
from setuptools import setup, find_packages

from glob import glob
from os.path import basename
from os.path import splitext

classifiers = [
    "Development Status :: 1 - Planning",
]

requires = [
    "sqlalchemy",
    "flask",
]

entry_points = {
    'console_scripts': [
        'pynuget = pynuget.cli:main',
    ],
}

setup(
    name="PyNuGet",
    version="0.0.1",

    description="A Python-based NuGet Server",
    long_description="TODO",
    url='https://github.com/dougthor42/pynuget/',
    license='MIT',

    author='Douglas Thor',
    author_email='doug.thor@gmail.com',


    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,

    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],

    classifiers=classifiers,

    python_requires=">=3.5",
    requires=requires,
    #tests_requrie=

    entry_points=entry_points
)
