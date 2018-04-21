# -*- coding: utf-8 -*-
"""
"""

from argparse import ArgumentParser

parser = ArgumentParser(description="PyNuGet")
parser.add_argument('--foo', action='store_true', help='foo help')



subparser = parser.add_subparser()

parser_init = subparsers.add_parser('init', help="init things")
parser_init.add_argument('--bar', action='store_true', help='do thing')

parser_clear = subparsers.add_parser('clear', help='remove all packages')
parser_clear.add_argument('--check', action='store_true')

