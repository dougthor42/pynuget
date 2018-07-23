# -*- coding: utf-8 -*-
"""
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

from glob import glob
from os.path import basename
from os.path import splitext


# #########################################################################
# These classes will only work if the user runs:
#    python setup.py develop
#    python setup.py install
class DevelopCommand(develop):
    """
    Modify the `develop` installation workflow.
    """
    def run(self):
        # Pre-install: nothing
        develop.run(self)
        # Post-install: perhaps init the dirs and database?


class InstallCommand(install):
    """
    Modify the starndard installation workflow.
    """
    def run(self):
        # Pre-install: nothing
        install.run(self)
        # Post-install: perhaps init the dirs and database?

# #########################################################################


classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    "Topic :: Software Development :: Build Tools",
]

requires = [
    "sqlalchemy>=1.2.7",
    "flask>=0.12.2",
    "lxml>=4.2.1",
    "requests>=2.19.1",
]

entry_points = {
    'console_scripts': [
        'pynuget = pynuget.cli:main',
    ],
}

with open("README.rst", 'r') as openf:
    long_description = openf.read()

setup(
    # General
    name="pynuget",
    version="0.1.0",

    # Descriptions
    description="A Python-based NuGet Server",
    long_description=long_description,
    long_description_content_type='text/x-rst',

    # Owner
    url='https://github.com/dougthor42/pynuget/',
    author='Douglas Thor',
    author_email='doug.thor@gmail.com',

    # Files
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,

    # these get copied to sys.prefix/data, which will be the venv's folder.
    data_files=[
        ('data', ['wsgi.py']),
        ('data', ['apache-example.conf']),
    ],

    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],

    classifiers=classifiers,

    # Versions and Requirements
    python_requires=">=3.5",
    install_requires=requires,
    #tests_requires=

    entry_points=entry_points,

    # https://stackoverflow.com/a/36902139/1354930
    cmdclass={
        'develop': DevelopCommand,
        'install': InstallCommand,
    },
)
