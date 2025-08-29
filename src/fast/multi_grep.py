#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import BOTTOM


def multi_grep(
    w: str,
    map_name_dfa: list,
    callback: callable = lambda name, j, k, w: None,
):
    """
    Searches sub-strings of a string matched by multiple patterns.

    Args:
        w (str): A ``str`` containing the word to process.
        map_name_dfa (dict): A ``dict{Name:  Automaton}`` mapping each pattern
            name with its corresponding DFA.
        callback (callable): A ``callable(Name, int, int, str)``
            called whenever ``w[j:k]`` is matched by pattern ``name``.
    """
    def make_map_name_q_js_next():
        return {
            name:  defaultdict(set)
            for (name, g) in map_name_dfa.items()
        }

    m = len(w)
    map_name_q_js = {
        name:  {g.initial():  {0}}
        for (name, g) in map_name_dfa.items()
    }

    map_name_q_js_next = make_map_name_q_js_next()
    for k in range(m):
        a = w[k]
        for (name, g) in map_name_dfa.items():
            map_q_js = map_name_q_js[name]
            for (q, js) in map_q_js.items():
                if not js:
                    continue
                r = g.delta(q, a)
                if r is BOTTOM:
                    map_name_q_js_next[name][q] = set()
                else:
                    map_name_q_js_next[name][r] |= map_q_js[q]
                    if g.is_final(r):
                        for j in js:
                            callback(name, j, k + 1, w)
            map_name_q_js_next[name][g.initial()] |= {k + 1}
        map_name_q_js = map_name_q_js_next
        map_name_q_js_next = make_map_name_q_js_next()


def multi_grep_with_delimiters(
    w: str,
    map_name_dfa: dict,
    callback: callable = lambda i, j, k, w: None,
    is_pattern_separator: callable = lambda name: False,
    is_pattern_left_separated: callable = lambda name: True,
    is_pattern_right_separated: callable = lambda name: True
):
    """
    Searches sub-strings of a string matched by multiple patterns, possibly
    delimited by a predefined collection of separator patterns.

    Args:
        w (str): A ``str`` containing the word to process.
        map_name_dfa (dict): A ``dict{Name:  Automaton}`` mapping each pattern
            name with its corresponding DFA.
        callback (callable): A ``callable(Name, int, int, str)``
            called whenever ``w[j:k]`` is matched by pattern ``name``.
        is_pattern_separator (callable): A ``callable(Name) -> bool``
            returning ``True`` iff the ``name`` pattern is a separator.
        is_pattern_left_separated (callable):  A ``callable(Name) -> bool``
            returning ``True`` iff the pattern ``name`` must be preceeded
            by a separator pattern or located at the beginning of ``w``.
        is_pattern_right_separated (callable): A ̀``callable(Name) -> bool``
            returning ``True`` iff the ``name`` pattern must be followed
            by a separator pattern or located at the end of ``w``.
    """
    # multi_grep on separating patterns
    map_name_dfa_separator = {
        name:  dfa
        for (name, dfa) in map_name_dfa.items()
        if is_pattern_separator(name)
    }
    functor_delims = MultiGrepFonctorLargest()
    multi_grep(w, map_name_dfa_separator, functor_delims)

    js = {0} | {
        k
        for (i, jks) in functor_delims.indices().items()
        for (j, k) in jks
    }

    ks = {len(w)} | {
        j
        for (i, jks) in functor_delims.indices().items()
        for (j, k) in jks
    }

    # multi_grep on other patterns
    def filtered_callback(name, j, k, w):
        if is_pattern_separator(name):
            return
        elif j not in js and is_pattern_left_separated(name):
            return
        elif k not in ks and is_pattern_right_separated(name):
            return
        else:
            callback(name, j, k, w)

    multi_grep(
        w,
        map_name_dfa,
        callback=lambda name, j, k, w: filtered_callback(name, j, k, w)
    )


class MultiGrepFonctor:
    """
    Base class used to customize the behavior of the
    :py:func:`multi_grep` function.
    """

    def __call__(self, i, j, k, w):
        """
        Args:
            i (int): The DFA index.
            j (int): The index of the beginning of a substring catched
                by the DFA.
            k (int): The index of o the end of a substring catched by the DFA.
            w (str): The input string.
        """
        raise NotImplementedError

    def indices(self) -> dict:
        """
        Returns:
            A ``dict{i:  [(j, k)]}`` where:
            ``i`` is an ``int`` corresponding to a DFA identifier.
            ``j`` is an ``int`` corresponding to the beginning of
            substring catched by the DFA ``i``.
            ``k`` is an ``int`` corresponding to the end of
            a substring catched by the DFA ``i``.
        """
        raise NotImplementedError


class MultiGrepFonctorAll(MultiGrepFonctor):
    """
    The :py:class:`MultiGrepFonctorAll` class catches
    (for each pattern Pi and for each index j)
    each substring w[j:k] matching Pi.
    """
    def __init__(self):
        self.map_i_jk = defaultdict(list)

    def __call__(self, i, j, k, w):
        self.map_i_jk[i].append((j, k))

    def indices(self) -> dict:
        return self.map_i_jk


class MultiGrepFonctorLargest(MultiGrepFonctor):
    """
    The :py:class:`MultiGrepFonctorLargest` class
    catches (for each pattern Pi and for each index j)
    the largest w[j:k] matching Pi.
    """
    def __init__(self):
        self.map_i_j_k = defaultdict(lambda: defaultdict(lambda: None))

    def __call__(self, i, j, k, w):
        # As we read w from left to right, k > self.map_pattern_indices[i][j]
        self.map_i_j_k[i][j] = k

    def indices(self) -> dict:
        # Rebuild {i:  [(j, k)]} for each (i, j) pair
        result = defaultdict(list)
        for i in self.map_i_j_k:
            for k in set(self.map_i_j_k[i].values()):
                result[i] += [(
                    min(
                        j for j in self.map_i_j_k[i].keys()
                        if self.map_i_j_k[i][j] == k
                    ),
                    k
                )]
            result[i] = sorted(result[i])
        return result


class MultiGrepFonctorGreedy(MultiGrepFonctorLargest):
    """
    The :py:class:`MultiGrepFonctorGreedy` class
    catches (for each pattern Pi and for each index j)
    the largest  w[j′:k] matching Pi and s.t.  j′ < j.
    """
    def __init__(self):
        super().__init__()
        self.map_i_k_j = defaultdict(lambda: defaultdict(lambda: None))

    def __call__(self, i, j, k, w):
        j_ = self.map_i_k_j[i][k]
        if j_ is None or j < j_:
            self.map_i_k_j[i][k] = j
            super().__call__(i, j, k, w)
