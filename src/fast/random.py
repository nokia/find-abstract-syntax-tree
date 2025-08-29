#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from random import choice, randrange, random
from pybgl import (
    MAP_OPERATORS_RE,
    Ast,
    Automaton,
    EdgeDescriptor,
)


def reject_sampling(
    sample,
    repeat: bool = True,
    max_sampling: int = 1000
):
    """
    Reject sampling procedure.

    Args:
        sample (callable): A `Callback() -> Result` callback which
            draws a random sample. If it returns `None`, the sample
            is rejected.
        repeat (bool): Pass `True` to rerun sampling in case of reject.
        max_sampling (int): Maximum number of sampling. Pass `None`
            to continue sampling until finding a non-rejected value.
            Note that if `sample` always returns `None`, this results
            to an infinite loop.

    Returns:
        The sampled instances, ``None`` otherwise.
    """
    if repeat:
        if max_sampling:
            for _ in range(max_sampling):
                ret = sample()
                if ret is not None:
                    break
        else:
            ret = None
            while ret is None:
                ret = sample()
    else:
        ret = sample()
    return ret


def random_word_from_automaton(
    g: Automaton,
    p: float = 0.5,
    repeat: bool = True,
    max_sampling: int = 1000
) -> str:
    """
    Perform a uniform random walk over an `Automaton` to generate
    a word accepted by this `Automaton`.

    Args:
        g (Automaton): A DFA.
        p (float): A value in [0, 1] corresponding to the probability to
            stop once a final state is reached
        repeat (bool): Pass ``True`` to try again while the sample is rejected.
        max_sampling (int): Max number of reject samplings.
            If you pass ``None``, the algorithm continues until finding a
            sample, but depending on `p` and `g`, this may result to an
            infinite loop.

    Returns:
        A string representing the word discovered during the walk, or
        ``None`` if the walk led to a non-final state without successor.
    """
    def find_ith_edge(q: int, i: int, g: Automaton) -> EdgeDescriptor:
        for e in g.out_edges(q):
            if i == 0:
                break
            i -= 1
        return e

    def sample(g, p) -> str:
        q = g.initial()
        w = ""  # If we stop on q0
        while True:
            r = random()
            if g.is_final(q) and p <= r:
                return w
            d = g.out_degree(q)
            if not d:
                # Trapped! Reject to avoid biases.
                return None
            i = randrange(d)
            e = find_ith_edge(q, i, g)
            q = g.target(e)
            w += g.label(e)

    if not 0 <= p < 1:
        raise RuntimeError("p = %s must be a float between 0.0 and 1.0")

    return reject_sampling(partial(sample, g=g, p=p), repeat, max_sampling)


# def random_words_from_automata(
#     dfas: list,
#     num_words: int = 30,
#     max_length: float = float("inf"),
#     distribution_dfa: list = None,
#     p: float = 0.5,
#     repeat: bool = True,
#     max_sampling: int = 1000
# ) -> list:
#     """
#     Concatenates `num_words` random words.
#     Each words is randomly drawn by performing a random (uniform) walk
#     on an input automaton picked at random (uniform).
#
#     Args:
#         dfas: A `list` of `Automaton` instances.
#         num_words: An `int` to the number of drawn sub-words.
#         max_length: The maximum word length allowed once words
#             are concatenated.
#         distribution_dfa: A list mapping each `Automaton` of `dfas` with its
#             probability. `distribution_dfa` must sum to `1.0`. Pass `None`
#             for uniform distribution.
#         + parameters of `random_word_from_automaton`.
#     Returns:
#         A `list` of `str` resulting from the samplings.
#         Some elements of the list may be `None` in case of reject.
#     """
#     if distribution_dfa is None:
#         distribution_dfa = [1 / len(dfas) for _ in range(len(dfas))]
#     assert len(distribution_dfa) == len(dfas)
#     assert 0.99 < sum(distribution_dfa) < 1.01
#
#     def sample(dfas, num_words, repeat, max_sampling):
#         words = list()
#         for i in range(num_words):
#             g = choices(population=dfas, weights=distribution_dfa)[0]
#             w = random_word_from_automaton(g, p, repeat, max_sampling)
#             words.append(w)
#         return words if len("".join(words)) < max_length else None
#
#     return reject_sampling(
#         partial(sample, dfas, num_words, repeat, max_sampling),
#         repeat,
#         max_sampling
#     )


def random_ast(
    re_len: int,
    alphabet: list = None,
    map_operators: dict = MAP_OPERATORS_RE,
) -> tuple:
    """
    Returns a random AST and its root node.

    Args:
        re_len(int): The number of nodes of the AST of the output regular
            expression.
        alphabet(list): A ``list`` gathering the character of the alphabet
            of the regular expressions. Default to ``list('a...z')``.
        map_operators(dict): A ``dict{str: pybgl.shunting_yard_postfix.Op}``
            mapping each meta-character with its corresponding attributes.
            Defaults to ``pybgl.shunting_yard_postfix.MAP_OPERATORS_RE``.

    Returns:
        A ``tuple(pybgl.shunting_yard_postfix.Ast, int)`` gathering the
        output AST and its root node.
    """
    def random_ast_rec(re_len: int) -> tuple:
        if re_len == 1:
            a = choice(alphabet)
            root = ast.add_vertex(a)
        elif re_len == 2:
            a = choice(alphabet)
            operator = choice(unary_operators)
            child = ast.add_vertex(a)
            root = ast.add_vertex(operator)
            ast.add_edge(root, child)
        else:
            card = choice([1, 2])
            operator = (
                choice(binary_operators) if card == 2
                else choice(unary_operators)
            )
            root = ast.add_vertex(operator)
            if card == 2:
                re_len_left = randrange(1, re_len - 1)
                re_len_right = re_len - re_len_left - 1
                root_left = random_ast_rec(re_len_left)
                root_right = random_ast_rec(re_len_right)
                ast.add_edge(root, root_left)
                ast.add_edge(root, root_right)
            elif card == 1:
                root_child = random_ast_rec(re_len - 1)
                ast.add_edge(root, root_child)
        return root

    if not alphabet:
        alphabet = list(chr(i) for i in range(ord("a"), ord("z") + 1))
    if any(op_obj.cardinality > 2 for op_obj in map_operators.values()):
        raise NotImplementedError
    ast = Ast()
    unary_operators = None
    binary_operators = None
    if re_len >= 2:
        unary_operators = [
            operator
            for (operator, attrs) in map_operators.items()
            if attrs.cardinality == 1
        ]
        if re_len >= 3:
            binary_operators = [
                operator
                for (operator, attrs) in map_operators.items()
                if attrs.cardinality == 2
            ]
    ast.root = random_ast_rec(re_len)
    return ast
