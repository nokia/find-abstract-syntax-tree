#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .density import ast_density
from .pattern_automaton import PatternAutomaton
from .regexp_ast import RegexpAst


def make_additive_objective_func_for_str(
    examples: list,
    alphabet: list,
    map_pa_infix_re: dict = None,
    size_factor: float = 0.5,
    density_factor: float = 0.5,
) -> callable:
    """
    Makes an additive objective function, finding a tradeoff between
    accuracy and shortness.

    Args:
        examples (list): A `list` of :py:class:`PatternAutomaton`
            instances.
        alphabet (list): The `list` of `str`, where each `str` is
            a symbol alphabet (possibly a metacharacter identifying a
            :py:class:`PatternAutomaton`, like `"$date"`).
        map_pa_infix_re (dict): A ``dict{PatternAutomaton : str}``
            that maps each :py:class:`PatternAutomaton` to its
            corresponding infix regular expression.
        size_factor (float): The importance of the shortness,
            between `0.0` and `1.0`. The higher `size_factor`, the
            more important the size of the inferred regular expression.
        density_factor (float): The importance of the accuracy,
            between `0.0` and `1.0`. The higher `density_factor`,
            the more important the size of the inferred regular expression.
            Should be set to `1 - size_factor`.

    Returns:
        The corresponding `callable(ast, examples) -> float` objective
        function where:

        - `ast` is a candidate solution;
        - `examples` is the set of positive examples;
          the returned value is the objective function value given `ast`.
    """
    # TODO Merge size_factor and density_factor
    # examples_sizes = [len(example.w) for example in examples]
    # map_len_proba = {
    #     length:  examples_sizes.count(length) / len(examples_sizes)
    #     for length in set(examples_sizes)
    # }
    # max_len = max(examples_sizes)
    max_len = max(
        len(example.w) if isinstance(example, PatternAutomaton)
        else len(example)
        for example in examples
    )
    map_len_proba = {
        length: 1 / max_len for length in range(1, max_len + 1)
    }
    char_proba = 1 / len(alphabet)

    def objective_function(ast: RegexpAst, examples: list):
        size = ast.num_nodes
        density = ast_density(ast, map_len_proba, char_proba, map_pa_infix_re)
        return size_factor * size + density_factor * density

    return objective_function


def make_normalized_additive_objective_func_for_str(
    examples: list,
    alphabet: list,
    map_pa_infix_re: dict = None,
    size_factor: float = 0.5,
    density_factor: float = 0.5,
) -> callable:
    """
    Makes a normalized additive objective function, finding a tradeoff
    between accuracy and shortness.

    Args:
        examples (list): A `list` of :py:class:`PatternAutomaton` instances.
        alphabet (list): The `list` of `str`, where each `str` is a symbol
            alphabet (possibly a metacharacter identifying a
            :py:class:`PatternAutomaton`, like `"$date"`).
        map_pa_infix_re (dict): A ``dict{PatternAutomaton : str}`` that maps
            each :py:class:`PatternAutomaton` to its corresponding
            regular expression.
        size_factor (float): The importance of the shortness, between `0.0`
            and `1.0`. The higher `size_factor`, the more important the size
            of the inferred regular expression.
        density_factor (float): The importance of the accuracy, between `0.0`
            and `1.0`. The higher `density_factor`, the more important the
            size of the inferred regular expression.
            Should be set to `1 - size_factor`.

    Returns:
        The corresponding `callable(ast, examples) -> float` objective
        function where:

        - `ast` is a candidate solution;
        - `examples` is the set of positive examples;
           the returned value is the objective function value given `ast`.
    """
    # TODO Merge size_factor and density_factor
    examples_sizes = [
        len(example.w) if isinstance(example, PatternAutomaton)
        else len(example)
        for example in examples
    ]

    # examples_sizes = [len(example.w) for example in examples]
    total_examples_size = sum(examples_sizes) + len(examples_sizes) + 1
    map_len_proba = {
        length: examples_sizes.count(length) / len(examples_sizes)
        for length in set(examples_sizes)
    }
    char_proba = 1 / len(alphabet)

    def objective_function(ast: RegexpAst, examples: list):
        # TODO remove `examples` parameter which is useless
        size = ast.num_nodes
        density = ast_density(ast, map_len_proba, char_proba, map_pa_infix_re)
        return (
            size_factor * (size / total_examples_size)
            + density_factor * density
        )

    return objective_function


def make_multiplicative_objective_func_for_str(
    examples,
    alphabet,
    map_pa_infix_re: dict = None,
    size_exponent=1,
    density_exponent=1,
) -> callable:
    """
    Makes a multiplicative objective function, finding a tradeoff between
    accuracy and shortness.

    Args:
        examples (list): A `list` of :py:class:`PatternAutomaton` instances.
        alphabet (list): The `list` of `str`, where each `str` is a symbol
            alphabet (possibly a metacharacter identifying a
            :py:class:`PatternAutomaton`, like `"$date"`).
        map_pa_infix_re (dict): A ``dict{PatternAutomaton : str}`` that maps
            each :py:class:`PatternAutomaton` to its corresponding
            regular expression.
        size_exponent (float): The importance of the shortness, between
            `0.0` and `1.0`. The higher `size_exponent`, the more important
            the size of the inferred regular expression.
        density_exponent (float): The importance of the accuracy, between
            `0.0` and `1.0`. The higher `density_exponent`, the more important
            the size of the inferred regular expression.
            Should be set to `size_exponent - 1`.

    Returns:
        The corresponding `callable(ast, examples) -> float` objective
        function where:

        - `ast` is a candidate solution;
        - `examples` is the set of positive examples;
          the returned value is the objective function value given `ast`.
    """
    # TODO Merge size_exponent and density_exponent
    EPSILON = 1E-6
    examples_sizes = [len(example.w) for example in examples]
    map_len_proba = {
        length:  examples_sizes.count(length) / len(examples_sizes)
        for length in set(examples_sizes)
    }
    char_proba = 1 / len(alphabet)

    def objective_function(ast: RegexpAst, examples: list) -> float:
        # TODO remove `examples` parameter which is useless
        size = ast.num_nodes
        density = ast_density(ast, map_len_proba, char_proba, map_pa_infix_re)
        return (
            max(EPSILON, size ** size_exponent) * density ** density_exponent
        )

    return objective_function


def make_tuple_based_objective_func_for_str(
    examples: list,
    alphabet: set,
    map_pa_infix_re: dict = None,
):
    """
    Makes a lexicographic objective function, finding a tradeoff between
    accuracy and shortness.

    Args:
        examples (list): A `list` of :py:class:`PatternAutomaton` instances.
        alphabet (list): The `list` of `str`, where each `str` is a symbol
            alphabet (possibly a metacharacter identifying a
            :py:class:`PatternAutomaton`, like `"$date"`).
        map_pa_infix_re (dict): A ``dict{PatternAutomaton : str}`` that maps
            each :py:class:`PatternAutomaton` to its corresponding regular
            expression.

    Returns:
        The corresponding `callable(ast, examples) -> float` objective
        function where:

        - `ast` is a candidate solution;
        - `examples` is the set of positive examples;
          the returned value is the objective function value given `ast`.
    """
    examples_sizes = [len(example.w) for example in examples]
    map_len_proba = {
        length:  examples_sizes.count(length) / len(examples_sizes)
        for length in set(examples_sizes)
    }
    char_proba = 1 / len(alphabet)

    def objective_function(ast: RegexpAst, examples: list) -> tuple:
        # TODO remove `examples` parameter which is useless
        size = ast.num_nodes
        density = ast_density(ast, map_len_proba, char_proba, map_pa_infix_re)
        return (size, density)

    return objective_function
