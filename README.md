# fAST (find Abstract Syntax Tree)

[![PyPI](https://img.shields.io/pypi/v/find_abstract_syntax_tree.svg)](https://pypi.python.org/pypi/find-abstract-syntax-tree)
[![Build](https://github.com/nokia/find-abstract-syntax-tree/workflows/build/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/build.yml)
[![Documentation](https://github.com/nokia/find-abstract-syntax-tree/workflows/docs/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/docs.yml)
[![ReadTheDocs](https://readthedocs.org/projects/find-abstract-syntax-tree/badge/?version=latest)](https://find-abstract-syntax-tree.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/nokia/find-abstract-syntax-tree/branch/master/graph/badge.svg?token=OZM4J0Y2VL)](https://codecov.io/gh/nokia/find-abstract-syntax-tree)

## Overview

[find-abstract-syntax-tree](https://github.com/nokia/find-abstract-syntax-tree) is a [Python 3](http://python.org/) implemention of the fAST algorithm. This algorithm aims at inferring a regular expression from a finite set of positive examples.

The fAST algorithm is described in:

[[ICGI'2023](https://icgi2023.inria.fr/)] fAST: regular expression inference from positive examples using Abstract Syntax Trees, Maxime Raynal, Marc-Olivier Buob, Georges Quénot.

This module is built on top of:
* [numpy](https://pypi.org/project/numpy/);
* [pybgl](https://pypi.org/project/pybgl/), a lightweight graph library.

## Links

* [Installation](https://github.com/nokia/find-abstract-syntax-tree/blob/master/docs/installation.md)
* [Documentation](https://find-abstract-syntax-tree.readthedocs.io/en/latest/)
* [Coverage](https://app.codecov.io/gh/nokia/find-abstract-syntax-tree)
* [Wiki](https://github.com/nokia/find-abstract-syntax-tree/wiki)

## License

This project is licensed under the [BSD-3-Clause license](https://github.com/nokia/find-abstract-syntax-tree/blob/master/LICENSE).
