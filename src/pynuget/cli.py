# -*- coding: utf-8 -*-
"""
"""

import sys
from argparse import ArgumentParser


def main():
    """
    """
    # Parent parser (common args).
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help=("Increase the verbosity. Can be supplied multiple times."
              " Max value: -vv"),
        default=0,
    )

    parent_parser.add_argument(
        '-V', "--version",
        action='store_true',
        help="Print the version number and exit.",
    )

    # Main parser
    parser = ArgumentParser(
        description="Administer the PyNuGet Server.",
        parents=[parent_parser],
    )

    # Subparsers ###########################################################
    subparser = parser.add_subparsers(
        title='subcommands',
        dest="verb",
    )

    # Init
    parser_init = subparser.add_parser(
        'init',
        help=("Create necessary folders and files. Copy Apache configuration"
              " template if one doesn't already exist."),
        parents=[parent_parser],
    )
    parser_init.add_argument(
        "--apache-config",
        help=("Define a custom name for the Apache configuation file."
              " Defaults to 'pynuget.conf'."),
        default="pynuget.conf",
    )
    parser_init.add_argument(
        "--server-path",
        help=("The path that the server should live at. Must be an absolute"
              " path. Defaults to '/var/www/pynuget'"),
        default="/var/www/pynuget",
    )
    parser_init.add_argument(
        "--package-dir",
        help=("The directory that the packages will be saved in and served"
              " from. If this value is not an absolute path, `server_path`"
              " will be used as the root. Defaults to 'packages' in"
              " `server_path`"),
        default="nuget_packages",
    )
    parser_init.add_argument(
        "--db-name",
        help=("The name of the database to use. If `db_backend` == 'sqlite',"
              " then this is the relative or absolute path to the SQLite file"
              " to use. If `db_backend` != 'sqlite', then this is the name of"
              " the Schema to create. Defaults to 'nuget_packages.sqlite' in"
              " `server_path`."),
        default="nuget_packages.sqlite",
    )
    parser_init.add_argument(
        "--db-backend",
        help=("What database backend to use. Defaults to 'sqlite'."),
        default="sqlite",
        choices=["sqlite", "mysql", "postgresql"],
    )

    # Clear
    parser_clear = subparser.add_parser(
        "clear",
        help=("Delete all packages and empty the package database. Basically"
              " resets things to a fresh install but does not change any"
              " settings."),
        parents=[parent_parser],
    )
    parser_clear.add_argument(
        '-y', "--yes",
        help=("Ignore the confirmation prompt and delete everything."),
        action='store_true',
    )

    # Parse the args
    args = parser.parse_args()

    # Show help when no commands or flags are given.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    # Run the function
    print(args)
