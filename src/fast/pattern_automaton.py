#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from functools import partial
from pybgl.automaton import Automaton, EdgeDescriptor
from pybgl.deterministic_inclusion import deterministic_inclusion
from pybgl.dijkstra_shortest_paths import dijkstra_shortest_path, make_path
from pybgl.property_map import (
    ReadPropertyMap, make_assoc_property_map, make_func_property_map
)
from .multi_grep import MultiGrepFonctorLargest, multi_grep


# Can possibly drops some arcs, e.g. "spaces" arcs
class PatternAutomaton(Automaton):
    """
    A PatternAutomaton models a string at the pattern level using a automaton-like structure
    whose vertices corresponds to a subset of string indices and arcs corresponds to infixes
    and their related pattern.
    """
    def __init__(
        self,
        word: str,
        map_name_dfa: dict,
        make_mg: callable = None,
        filtered_patterns = None
    ):
        """
        Constructs the `PatternAutomaton` related to an input words according
        to a collection of patterns and according to a `multi_grep` stategy.

        Args:
            word: An `str` instance.
            map_name_dfa: A `dict{str: Automaton}` mapping each relevant type with its
                corresponding `Automaton` instance.
            filtered_patterns: A subset (possibly empty) of `map_name_dfa.keys()` of type
                that must be catched my multi_grep, but not reflected as arcs in the
                `PatternAutomaton`. It can be used e.g. to drop spaces an get a smaller
                `PatternAutomaton`, but the position of spaces in the original lines will be lost.
        """
        if filtered_patterns is None:
#            filtered_patterns = {"spaces"} # This will pose problem to transform PA to regexp
            filtered_patterns = set()
        if not make_mg:
            make_mg = MultiGrepFonctorLargest
        mg = make_mg()

        pattern_names = list(map_name_dfa.keys())

        # Add vertices
        n = len(word)
        super().__init__(n + 1)
        self.set_final(n)
        self.w = word

        # Add edges
        multi_grep(word, map_name_dfa, mg)
        if mg.indices():
            vertices_with_successors = set()
            vertices_with_predecessors = set()
            for (name, jks) in mg.indices().items():
                if name in filtered_patterns:
                    continue
                for (j, k) in jks:
                    self.add_edge(j, k, name)
                    vertices_with_successors.add(j)
                    vertices_with_predecessors.add(k)
            to_keep = sorted(vertices_with_successors | vertices_with_predecessors | {0, n})

            # Remove isolated vertices
            for u in range(n):
                if u not in to_keep:
                    self.remove_vertex(u)

            # Add missing "any" edges
            for (i, u) in enumerate(to_keep):
                if u != 0 and u not in vertices_with_predecessors:
                    self.add_edge(to_keep[i-1], u, "any")
                if u != n and u not in vertices_with_successors:
                    self.add_edge(u, to_keep[i+1], "any")
        else:
            # The PatternAutomaton involves a single "any" arc
            to_remove = set()
            for u in self.vertices():
                if u not in {0, n}:
                    to_remove.add(u)
            for u in to_remove:
                self.remove_vertex(u)
            if len(word):
                self.add_edge(0, len(word), "any")

    def get_slice(self, e) -> tuple:
        """
        Retrieves the slice (pair of uint indices) related to an edge.

        Returns:
            The slice related to an arbitrary edge of this PatternAutomaton instance.
        """
        j = self.source(e)
        k = self.target(e)
        return (j, k)

    def get_infix(self, e: EdgeDescriptor) -> str:
        """
        Retrieves the infix (substring) related to an edge.

        Returns:
            The infix related to an arbitrary edge of this PatternAutomaton instance.
        """
        (j, k) = self.get_slice(e)
        return self.w[j:k]

    def __eq__(self, pa) -> bool:
        """
        Equality operator. This implementation assumes
        that `PatternAutomaton` using `MultiGrepFonctorLargest` or
        `MultiGrepFonctorLargest` are minimal.

        Args:
            pa: A `PatternAutomaton` instance.
        Returns:
            True iff `self` matches another `PatternAutomaton` instance.
        """
        if self.num_vertices() != pa.num_vertices() or self.num_edges() != pa.num_edges():
            # MultiGrepFonctorLargest guarantees that two PatternAutomaton can
            # only be equal if they are of same size, because PatternAutomaton are
            # always minimal.
            return False
        return deterministic_inclusion(self, pa) == 0


def pattern_automaton_edge_weight(
    e: EdgeDescriptor,
    g: PatternAutomaton,
    map_name_density: dict = None
) -> float:
    a = g.label(e)
    return map_name_density.get(a, 1.0) if map_name_density else 1.0


def pattern_automaton_to_path(g: PatternAutomaton, *cls, **kwargs) -> list:
    """
    Extracts from a :py:class:`PatternAutomaton` instance the most relevant
    path (highlighting the most relevant pattern-based decomposition).

    Args:
        g (PatternAutomaton): The considered :py:class:`PatternAutomaton`
            instance.
        cls, kwargs: See the :py:func:`pybgl.dijkstra_shortest_path` function.
    """
    s = g.initial()
    f = g.finals()
    assert len(f) == 1
    t = f.pop()

    pmap_vpreds = kwargs.pop("pmap_vpreds", None)
    if pmap_vpreds is None:
        map_vpreds = defaultdict(set)
        pmap_vpreds = make_assoc_property_map(map_vpreds)
    pmap_vdist = kwargs.pop("pmap_vdist", None)
    if pmap_vdist is None:
        map_vdist = dict()
        pmap_vdist = make_assoc_property_map(map_vdist)
    pmap_eweight = kwargs.pop("pmap_eweight", None)
    map_name_density = kwargs.pop("map_name_density", None)
    assert pmap_eweight or map_name_density
    if pmap_eweight is None:
        pmap_eweight = make_func_property_map(
            partial(
                pattern_automaton_edge_weight,
                g=g,
                map_name_density=map_name_density
            )
        )

    dijkstra_shortest_path(
        g, s, t,
        pmap_eweight,
        pmap_vpreds,
        pmap_vdist,
        **kwargs
    )
    return make_path(g, s, t, map_vpreds)
