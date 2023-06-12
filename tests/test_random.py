#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.regexp import compile_dfa
from fast.random import random_word_from_automaton
from fast.regexp import RE_IPV4


def test_random_word_from_automaton():
    g = compile_dfa(RE_IPV4)
    for _ in range(5):
        w = random_word_from_automaton(g, p=0.5, max_sampling=None)
        assert g.accepts(w)
