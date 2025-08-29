#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Top-level package."""

__author__ = "Maxime Raynal, Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__ = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__ = "Copyright (C) 2023, Nokia"
__license__ = "BSD-3"
__version__ = '0.2.1'  # Use single quotes for bumpversion (see setup.cfg)

from .cbfs import CBFS
from .density import ast_density, dfa_density
from .fast import fast, fast_from_re, fast_from_strings, fast_benchmark
from .multi_grep import (
    MultiGrepFonctorAll,
    MultiGrepFonctorLargest,
    MultiGrepFonctorGreedy,
    multi_grep, multi_grep_with_delimiters
)
# from .objective_func.py import ...
from .pattern_automaton import PatternAutomaton
from .random import random_ast, random_word_from_automaton
from .regexp_ast import RegexpAst
# from .regexp_mutators import ...
