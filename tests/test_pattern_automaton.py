#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from fast.regexp import make_map_name_dfa
from fast.pattern_automaton import PatternAutomaton

MAP_NAME_DFA = make_map_name_dfa(["float", "int", "ipv4", "spaces", "uint"])


def test_pattern_automaton():
    w = "11.22.33.44 55.66 789"
    g = PatternAutomaton(w, MAP_NAME_DFA)

    assert g.initial() == 0
    assert g.is_final(len(w))
    assert g.num_vertices() == 14
    assert g.num_edges() == 26


def test_pattern_automaton_empty_word():
    w = ""
    g = PatternAutomaton(w, MAP_NAME_DFA)
    assert g.num_vertices() == 1
    assert g.num_edges() == 0
    assert g.is_final(0)


def test_pattern_automaton_equals():
    g1 = PatternAutomaton("11.22.33.44 55.66 789", MAP_NAME_DFA)
    g2 = PatternAutomaton("55.66.77.88 9876 55.44", MAP_NAME_DFA)
    g3 = PatternAutomaton("1.2.3.4 77.88 90", MAP_NAME_DFA)
    assert g1 != g2
    assert g1 == g3


def test_pattern_automaton_get_slice():
    w = "10   abc  1.2.3.4  de 56.78"
    g = PatternAutomaton(w, MAP_NAME_DFA)
    types = {g.label(e) for e in sorted(g.edges())}
    expected = {"ipv4", "int", "float", "any", "spaces", "uint"}
    assert types == expected
    slices = [g.get_slice(e) for e in sorted(g.edges())]
    expected = [
        (0, 2),    # float
        (0, 2),    # int
        (0, 2),    # uint
        (2, 5),    # spaces
        (5, 8),    # any
        (8, 10),   # spaces
        (10, 11),  # int
        (10, 11),  # uint
        (10, 13),  # float
        (10, 17),  # ipv4
        (11, 12),  # any
        (12, 13),  # int
        (12, 13),  # uint
        (12, 15),  # float
        (13, 14),  # any
        (14, 15),  # uint
        (14, 15),  # int
        (14, 17),  # float
        (15, 16),  # any
        (16, 17),  # uint
        (16, 17),  # float
        (17, 19),  # spaces
        (19, 21),  # any
        (21, 22),  # spaces
        (22, 24),  # int
        (22, 24),  # uint
        (22, 27),  # float
        (24, 25),  # any
        (25, 27),  # int
        (25, 27),  # uint
    ]
    assert slices == expected
    infixes = [g.get_infix(e) for e in sorted(g.edges())]
    expected = [
        "10",       # float
        "10",       # int
        "10",       # uint
        "   ",      # spaces
        "abc",      # any
        "  ",       # spaces
        "1",        # int
        "1",        # uint
        "1.2",      # float
        "1.2.3.4",  # ipv4
        ".",        # any
        "2",        # int
        "2",        # uint
        "2.3",      # float
        ".",        # any
        "3",        # int
        "3",        # uint
        "3.4",      # float
        ".",        # any
        "4",        # int
        "4",        # uint
        "  ",       # spaces
        "de",       # any
        " ",        # spaces
        "56",       # int
        "56",       # uint
        "56.78",    # float
        ".",        # any
        "78",       # int
        "78",       # uint
    ]
    assert infixes == expected
