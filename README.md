# fAST (find Abstract Syntax Tree)

[![PyPI](https://img.shields.io/pypi/v/find_abstract_syntax_tree.svg)](https://pypi.python.org/pypi/find-abstract-syntax-tree)
[![Build](https://github.com/nokia/find-abstract-syntax-tree/workflows/build/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/build.yml)
[![Documentation](https://github.com/nokia/find-abstract-syntax-tree/workflows/docs/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/docs.yml)
[![ReadTheDocs](https://readthedocs.org/projects/find-abstract-syntax-tree/badge/?version=latest)](https://find-abstract-syntax-tree.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/nokia/find-abstract-syntax-tree/branch/main/graph/badge.svg?token=I7FEGOOYFG)](https://codecov.io/gh/nokia/find-abstract-syntax-tree)

## Overview

[find-abstract-syntax-tree](https://github.com/nokia/find-abstract-syntax-tree) is a [Python 3](http://python.org/) implemention of the fAST algorithm. This algorithm aims at inferring a regular expression from a finite set of positive examples.

The fAST algorithm is described in:

[[ICGI'2023](https://icgi2023.inria.fr/)] fAST: regular expression inference from positive examples using Abstract Syntax Trees, [Maxime Raynal](https://raynalm.github.io/), [Marc-Olivier Buob](https://www.bell-labs.com/about/researcher-profiles/marc-olivier-buob/), [Georges Quénot](http://mrim.imag.fr/georges.quenot/).

This module is built on top of:
* [numpy](https://pypi.org/project/numpy/);
* [pybgl](https://pypi.org/project/pybgl/), a lightweight graph library.

## Quick start

Install the package through PIP:
```bash
pip3 install find-abstract-syntax-tree
```
In your python interpreter, run:
```python
from fast import fast

results = fast(["abc", "abcabc", "abcabcabc"])
for (score, ast) in results:
    print(score, ast.to_infix_regexp_str())
```

## Links

* [Installation](https://github.com/nokia/find-abstract-syntax-tree/blob/master/docs/installation.md)
* [Documentation](https://find-abstract-syntax-tree.readthedocs.io/en/latest/)
* [Coverage](https://app.codecov.io/gh/nokia/find-abstract-syntax-tree)
* [Wiki](https://github.com/nokia/find-abstract-syntax-tree/wiki)

## License

This project is licensed under the [BSD-3-Clause license](https://github.com/nokia/find-abstract-syntax-tree/blob/master/LICENSE).
