#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pybgl import Automaton, compile_dfa
# from .brzozowski_minimization import brzozowski_minimization
from .regexp_ast import RegexpAst


def dfa_density(dfa: Automaton, length: int, char_proba: float):
    """
    Computes the ratio of the number of words of length ``length``
    accepted by an automaton ``dfa``, over the number of words of
    length ``length``.
    This corresponds to the density of ``a`` if we restrict to the
    words of length ``length``.

    Args:
        dfa (Automaton): A :py:class:`pybgl.Automaton` instance.
        length (int): The considered length. Must be a positive
            integer.
        char_proba (float): The probability to pick a given character
            in the alphabet.
            Should probably be set to ``1 / len(dfa.alphabet())`` ?

    Returns:
        The density of ``a`` if we restrict to the words of length ``length``.
    """
    # TODO: this is a kind of pagerank assuming that DFA is acyclic, but the
    # results depends on the order the vertices are visited.
    # So the implementation  below is inaccurate.
    # TODO: remove char_proba parameter.
    map_q_proba = {
        q: 1 if dfa.is_initial(q) else 0
        for q in dfa.vertices()
    }
    for _ in range(length):
        new_map_q_proba = {q: 0 for q in dfa.vertices()}
        for (q, adj_q) in dfa.adjacencies.items():
            for (a, r) in adj_q.items():
                new_map_q_proba[r] += char_proba * map_q_proba[q]
        map_q_proba = new_map_q_proba
    return sum(
        map_q_proba[q] if dfa.is_final(q) else 0
        for q in dfa.vertices()
    )


def ast_density(
    ast: RegexpAst,
    map_len_proba: dict,
    char_proba: float,
    map_pa_infix_re: dict = None
) -> float:
    """
    Compute the density related to a given regular expression
    abstract syntax tree.

    Args:
        ast (RegexpAst): A :py:class:`RegexpAst` instance.
        map_len_proba (dict):
        char_proba (float): The probability to pick a given character
            in the alphabet.
            Should probably be set to ``1 / len(dfa.alphabet())`` ?
        map_pa_infix_re (dict): A ``dict{PatternAutomaton : str}`` that maps
            each :py:class:`PatternAutomaton` to its corresponding
            regular expression.

    Returns:
        The density of ``ast``.
    """
    # print(map_len_proba)
    # print("     Computing density of %s" % ast.to_prefix_regexp_str())
    infix_regexp = ast.to_infix_regexp_str().replace(".", "")
    # print("     %s" % map_pa_infix_re)
    # print("     before replacing: %s" % infix_regexp)
    if map_pa_infix_re:
        for (pa, infix_re) in map_pa_infix_re.items():
            infix_regexp = infix_regexp.replace(pa, "(" + infix_re + ")")
    # print("     after replacing: %s" % infix_regexp)
    dfa = compile_dfa(infix_regexp)
    # mini_dfa = brzozowski_minimization(dfa)
    map_example_len_density = {
        # length: dfa_density(mini_dfa, length, char_proba)
        length: dfa_density(dfa, length, char_proba)
        for length in map_len_proba.keys()
    }
    result = sum(
        map_example_len_density[length] * map_len_proba[length]
        for length in map_len_proba.keys()
    )
    # print("        Done, density = %s" % result)
    return result
