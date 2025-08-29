#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque
from copy import deepcopy
from pybgl import (
    EdgeDescriptor,
    enrich_kwargs,
    make_func_property_map,
    ipynb_display_graph,
    to_dot,
)
from .pattern_automaton import PatternAutomaton


class RegexpAst:
    """
    n-ary representations of a regular expression AST.
    Do not use binary AST otherwise the priority queue will explode!
    Note that calling simplify transforms an arbitrary AST to a n-ary AST.
    """
    ROOT = "root"  # TODO ROOT = "&perp;"

    def __init__(self):
        """
        Constructor.
        """
        self.num_nodes = 0
        # Counts the actual number of nodes
        self.nodes_id = 0
        # Node ID for next new node
        self.map_node_label = dict()
        # Maps vertex to its label
        self.map_node_parent = dict()
        # Maps a vertex to its parent node # TODO use defaultdict(lambda: None)
        self.map_node_children = dict()
        # Maps a vertex to its child(ren) (if any) # TODO use defaultdict(list)

        # Create a root node
        self.root = self.add_node(label=self.ROOT)
        self.set_child(self.root, None)

    # TODO rename to add_vertex
    def add_node(self, label: str) -> int:
        """
        Add a new node to this AST.

        Args:
            label (str): The label of the added node.

        Returns:
            The newly added vertex descriptor.
        """
        new_node = self.nodes_id
        self.map_node_label[new_node] = label
        self.map_node_children[new_node] = []
        self.map_node_parent[new_node] = None
        self.nodes_id += 1
        self.num_nodes += 1
        return new_node

    # TODO rename to remove_vertex
    def remove_node(self, u: int):
        """
        Removes a node from this :py:class:`RegexpAst` instance.

        Args:
            u (int): The vertex descriptor of the node to be removed.
        """
        del self.map_node_label[u]
        del self.map_node_parent[u]
        del self.map_node_children[u]
        self.num_nodes -= 1

    def is_downwards_arc(self, u: int, v: int) -> bool:
        """
        Checks whether an ``(u, v)`` arc is downward
        (i.e., if ``v`` is a child of ``u``).

        Args:
            u (int): The vertex descriptor of the source of the arc.
            v (int): The vertex descriptor of the target of the arc.

        Returns:
            ``True`` iff ``(u, v)`` is downward.
        """
        return self.map_node_parent[v] == u

    def is_upwards_arc(self, u: int, v: int) -> bool:
        """
        Checks whether an ``(u, v)`` arc is upward
        (i.e., if ``u`` is a child of ``v``).

        Args:
            u (int): The vertex descriptor of the source of the arc.
            v (int): The vertex descriptor of the target of the arc.

        Returns:
            ``True`` iff ``(u, v)`` is upward, ``False`` otherwise.
        """
        return self.is_downwards_arc(v, u)

    # TODO why not using len(self.map_node_children) == 1 ?
    def is_unary(self, u: int) -> bool:
        """
        Checks whether a node is unary.
        It concerns nodes labeled by an unary regular expression operator
        (i.e., "+", "*", "?") and the root of this
        :py:class:``RegexpAst`` instance.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            ``True`` iff ``u`` is unary, ``False`` otherwise.
        """
        return self.map_node_label[u] in {"+", "*", "?", self.ROOT}

    # TODO why not using len(self.map_node_children) > 1 ?
    def is_n_ary(self, u: int) -> bool:
        """
        Checks whether a node is ``n``-ary, ``n > 1``.
        It concerns nodes labeled by an ``n``-ary regular expression operator
        (i.e., ".", "|") and the root of this :py:class:``RegexpAst`` instance.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            ``True`` iff ``u`` is ``n``-ary, ``False`` otherwise.
        """
        return self.map_node_label[u] in {".", "|"}

    # TODO why not using len(self.map_node_children) == 0 ?
    def is_leaf(self, u: int) -> bool:
        """
        Checks whether a node is a leaf.
        It concerns nodes labeled by a symbol of the alphabet.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            ``True`` iff ``u`` is a leaf, ``False`` otherwise.
        """
        return not self.is_n_ary(u) and not self.is_unary(u)

    def get_arc_index(self, u: int, v: int) -> int:
        """If (u,v) is downwards, and v is the i^th child of u, returns i.
        If (u,v) is upwards, and u is the i^th child of v, returns i."""
        if self.is_upwards_arc(u, v):
            return self.get_arc_index(v, u)
        return self.map_node_children[u].index(v)

    def label(self, u) -> str:
        """
        Retrieves the label of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The label of ``u``.
        """
        return self.map_node_label[u]

    def set_label(self, u: int, label: str):
        """
        Sets the label of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.
            label (str): Set the label of a given node.
        """
        self.map_node_label[u] = label

    def parent(self, u: int) -> int:
        """
        Retrieves the parent of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The parent of ``u`` if any or ``None``.
        """
        return self.map_node_parent[u]

    def children(self, u: int) -> iter:
        """
        Retrieves the children of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The parent of ``u`` if any or ``None``.
        """
        return self.map_node_children[u]

    def first_child(self, u: int) -> int:
        """
        Retrieves the first child of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The vertex descriptor of the first child of ``u``.

        Raises:
            `IndexError`: if the node is a leaf.
                See also the :py:meth:`RegexpAst.is_leaf` method.
        """
        return self.map_node_children[u][0]

    def ith_child(self, u: int, i: int) -> int:
        """
        Retrieves the ``i``-th child of a given vertex.

        Args:
            u (int): The vertex descriptor of the considered node.
            i (int): The child index.

        Returns:
            The vertex descriptor of the ``i``-th child of ``u``.

        Raises:
            `IndexError`: if the node is a leaf.
                See also the :py:meth:`RegexpAst.is_leaf` method.
        """
        return self.map_node_children[u][i]

    # TODO why v ?
    def is_last_child(self, u: int, v: int) -> bool:
        """
        Checks whether ``u`` is the last child of ``v``.

        Args:
            u (int): The vertex descriptor of the considered children.
            v (int): The vertex descriptor of the parent node of ``u``.

        Returns:
            ``True`` if and only if ``u`` is the last child of ``v``.
        """
        return self.map_node_children[v][-1] == u

    def set_child(self, u: int, v: int, set_parent: bool = True):
        """
        Sets ``v`` as the only child of ``u``.

        Args:
            u (int): The vertex descriptor of the parent node.
            v (int): The vertex descriptor of the child node.
            set_parent (bool): Pass ``True`` to update the parent of ``v``.
                Defaults to ``True``.
        """
        self.map_node_children[u] = [v]
        if set_parent:
            self.map_node_parent[v] = u

    def set_children(self, u: int, vs: iter, set_parents: bool = True):
        """
        Sets the children of ``u``.

        Args:
            u (int): The vertex descriptor of the parent node.
            vs (iter): The vertex descriptors of the child nodes.
            set_parent (bool): Pass ``True`` to update the parent of ``v``.
                Defaults to ``True``.
        """
        self.map_node_children[u] = vs
        if set_parents:
            for v in vs:
                self.map_node_parent[v] = u

    def set_ith_child(self, u: int, v: int, i: int, set_parent: bool = True):
        """
        Sets the ``i``-th children of ``u`` to ``v``.

        Args:
            u (int): The vertex descriptor of the parent node.
            v (int): The vertex descriptor of the child node.
            i (int): The child index. It must verify
               ``0 < i <= self.num_children(u)``.
            set_parent (bool): Pass ``True`` to update the parent of ``v``.
                Defaults to ``True``.

        Raises:
            `IndexError` if ``not (0 < i <= self.num_children(u))``
        """
        self.map_node_children[u][i] = v
        if set_parent:
            self.map_node_parent[v] = u

    def append_child(self, u: int, v: int, set_parent: bool = True):
        """
        Appends a new child to a node ``u``.

        Args:
            u (int): The vertex descriptor of the parent node.
            v (int): The vertex descriptor of the child node.
            set_parent (bool): Pass ``True`` to update the parent of ``v``.
                Defaults to ``True``.
        """
        self.map_node_children[u].append(v)
        if set_parent:
            self.map_node_parent[v] = u

    def num_children(self, u: int) -> int:
        """
        Retrieves the number of children of ``u``.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The number of children of ``u``.
        """
        return len(self.map_node_children[u])

    def is_ancestor_of(self, u: int, v: int) -> bool:
        """
        Tests if ``v`` is an ancestor of ``u``.

        Args:
            u (int): The vertex descriptor of a node.
            v (int): The vertex descriptor of the candidate ancestor.

        Returns:
            ``True`` iff ``v`` is an ancestor of ``u``, ``False`` otherwise.
        """
        # TODO we should use self.map_parent
        if self.is_leaf(u):
            return u == v
        elif self.is_unary(u):
            return self.is_ancestor_of(self.first_child(u), v)
        elif self.is_n_ary(u):
            return any(
                self.is_ancestor_of(u_child, v) for u_child in self.children(u)
            )

    def epsilon_successors(self, u: int, v: int) -> set:
        """
        Retrieves the out-edges of ``v`` that are epsilon-reachable from
        a ``(u, v)`` arc.
        See also :py:meth:`RegexpAst.epsilon_reachables`.

        Args:
            u (int): The source of the arc.
            v (int): The target of the arc.

        Returns:
            The set of out-edges of ``(u', v')`` arcs that are
            epsilon-reachable from the ``(u, v)`` arc
        """
        if v is None:
            assert u == self.root
            return {(u, self.first_child(u))}

        # print("**", u, v, self.map_node_parent[u], self.map_node_parent[v])
        result = set()
        result.add((u, v))
        v_label = self.label(v)
        if self.is_downwards_arc(u, v):
            # print("down")
            if v_label == "+":
                result.add((v, self.first_child(v)))
            elif v_label == "*" or v_label == "?":
                result.add((v, u))
                result.add((v, self.first_child(v)))
            elif v_label == ".":
                result.add((v, self.first_child(v)))
            elif v_label == "|":
                for child in self.children(v):
                    result.add((v, child))
            # case v is root or v is a leaf -> no epsilon successors

        else:
            # print("up")
            if v_label == "+" or v_label == "*":
                result.add((v, u))
                result.add((v, self.parent(v)))
            elif v_label == "?":
                result.add((v, self.parent(v)))
            elif v_label == ".":
                if self.is_last_child(u, v):
                    result.add((v, self.parent(v)))
                else:
                    u_index = self.get_arc_index(v, u)
                    result.add((v, self.ith_child(v, u_index + 1)))

            elif v_label == "|":
                result.add((v, self.parent(v)))
            # case v is root -> no eps successors
            # case v is leaf impossible
        # print("**", result)
        return result

    def epsilon_reachables(self, u: int, v: int = None) -> set:
        """
        Retrieves the edges that are epsilon-reachable from
        a ``(u, v)`` arc.
        See also :py:meth:`RegexpAst.epsilon_successors`.

        Args:
            u (int): The source of the arc.
            v (int): The target of the arc. If ``u`` is a leaf
                you may pass ``None``.

        Returns:
            The set of out-edges of ``(u', v')`` arcs that are
            epsilon-reachable from the ``(u, v)`` arc
        """
        # print("eps reach", u, v)
        result = set()
        stack = deque()
        result.add((u, v))
        stack.append((u, v))
        while len(stack) > 0:
            (u, v) = stack.pop()
            # print("__", u, v)
            for (uu, vv) in self.epsilon_successors(u, v):
                if (uu, vv) not in result:
                    # print("___adding___", uu, vv)
                    result.add((uu, vv))
                    stack.append((uu, vv))
        return result

    def to_prefix_regexp_str(self, u: int = None) -> str:
        """
        Builds the prefix regular expression of this
        :py:class:`RegexpAst` instance.
        See also :py:meth:`RegexpAst.to_prefix_regexp_list`.

        Args:
            u (int): Pass ``None``.

        Returns:
            A string storing the prefix regular expression modeling
            this :py:class:`RegexpAst` instance.
        """
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return ""
        u_label = self.label(u)
        if self.is_n_ary(u):
            return u_label + '(' + ','.join(
                [self.to_prefix_regexp_str(v) for v in self.children(u)]
            ) + ')'
        elif self.is_unary(u):
            return u_label + self.to_prefix_regexp_str(self.first_child(u))
        else:  # u is a leaf
            return u_label

    def to_prefix_regexp_list(self, u: int = None) -> list:
        """
        Builds the prefix regular expression of this
        :py:class:`RegexpAst` instance.
        See also :py:meth:`RegexpAst.to_prefix_regexp_str`.

        Args:
            u (int): Pass ``None``.

        Returns:
            A string storing the prefix regular expression modeling
            this :py:class:`RegexpAst` instance.
        """
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return []
        u_label = self.label(u)
        if self.is_n_ary(u):
            result = [u_label, '(']
            for v in self.children(u):
                if not v == self.first_child(u):
                    result += [',']
                result += self.to_prefix_regexp_list(v)
            result += [')']
            return result
        elif self.is_unary(u):
            return [u_label] \
                + self.to_prefix_regexp_list(self.map_node_children[u][0])
        else:  # u is a leaf
            return [u_label]

    def to_infix_regexp_str(self, u=None) -> str:
        """
        Builds the infix regular expression of this
        :py:class:`RegexpAst` instance.
        See also :py:meth:`RegexpAst.to_prefix_regexp_list`.

        Args:
            u (int): Pass ``None``.

        Returns:
            A string storing the prefix regular expression modeling
            this :py:class:`RegexpAst` instance.
        """
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                result = ""
        u_label = self.label(u)
        if self.is_n_ary(u):
            result = '(' * (len(self.children(u)) - 1) + u_label.join(
                [self.to_infix_regexp_str(v) + (')' if i > 0 else "")
                 for i, v in enumerate(self.children(u))]
            )
        elif self.is_unary(u):
            child_is_leaf = self.is_leaf(self.first_child(u))
            result = ("" if child_is_leaf else "(") \
                + self.to_infix_regexp_str(self.first_child(u)) \
                + ("" if child_is_leaf else ")") + u_label
        else:  # u is a leaf
            result = u_label
        if u == self.first_child(self.root):
            if result[0] == '(' and result[-1] == ')':
                result = result[1:-1]
        return result

    def copy(self):
        """
        Copy this :py:class:`RegexpAst` instance.

        Returns:
            A copy this :py:class:`RegexpAst` instance.
        """
        return deepcopy(self)

    def simplify(self, active_leaf: int = None):
        """
        Applies the following simplifications on this
        :py:class:`RegexpAst` instance.

        - :py:meth:`RegexpAst.simplify_unary_nodes`
        - :py:meth:`RegexpAst.simplify_n_ary_nodes`
        - :py:meth:`RegexpAst.reorder_or_nodes`
        - :py:meth:`remove_unary_n_aries`

        Args:
            active_leaf (int): Pass `None`
        """
        self.simplify_unary_nodes()  # ++ -> + ; ?? -> ? ,; ?+ -> * etc.
        self.simplify_n_ary_nodes()  # (a.b).c -> (a.b.c)
        self.reorder_or_nodes()      # b|a -> a|b
        # <<<
        # self.simplify_or_nodes(active_leaf=active_leaf)
        # MANDO: a | a -> a. Be cautious, do not remove if
        # a is the source of the active arc.
        # >>>
        self.remove_unary_n_aries()
        # When inserting unary node, some binary node may get
        # only one operand and hence become useless.
        # We just remove the useless operator. |a -> a ; .a -> a

    def simplify_unary_nodes(self, u=None):
        # print("8______start")
        # print(u)
        # ipynb_display_graph(self)
        # print("8______end")
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return

        if self.is_n_ary(u):
            for v in self.children(u):
                self.simplify_unary_nodes(v)

        elif self.is_unary(u):
            v = self.first_child(u)
            if self.is_unary(v):
                u_label = self.label(u)
                v_label = self.label(v)
                if u_label != v_label:
                    self.set_label(u, "*")
                # remove v
                v_child = self.first_child(v)
                self.set_child(u, v_child)
                self.remove_node(v)
                self.simplify_unary_nodes(u)
            else:
                self.simplify_unary_nodes(v)

    def merge_n_ary_nodes(self, u, v, remove_v=True):
        i = self.get_arc_index(u, v)
        self.map_node_children[u] = (
            self.map_node_children[u][:i]
            + self.map_node_children[v]
            + self.map_node_children[u][i+1:]
        )
        for v_child in self.children(v):
            self.map_node_parent[v_child] = u
        if remove_v:
            self.remove_node(v)

    def simplify_n_ary_nodes(self, u=None):
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return
        if self.is_unary(u):
            self.simplify_n_ary_nodes(self.first_child(u))

        elif self.is_n_ary(u):
            u_label = self.label(u)
            has_merged = False
            for i, v in enumerate(self.children(u)):
                v_label = self.label(v)
                if u_label == v_label:
                    self.merge_n_ary_nodes(u, v)
                    has_merged = True
                    break
            if has_merged:
                self.simplify_n_ary_nodes(u)
            else:
                for v in self.children(u):
                    self.simplify_n_ary_nodes(v)

    # UNUSED
    def simplify_or_nodes(self, active_leaf=None, u=None):
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return

        if self.is_unary(u):
            self.simplify_or_nodes(self.first_child(u))

        elif self.is_n_ary(u):
            for v in self.children(u):
                self.simplify_or_nodes(v)
            if self.label(u) == "|":
                children_prefixes = dict()
                to_remove = set()
                for v in self.children(u):
                    v_prefix = self.to_prefix_regexp_str(v)
                    if v_prefix in children_prefixes:
                        if self.is_ancestor_of(v, active_leaf):
                            to_remove.add(children_prefixes[v_prefix])
                            children_prefixes[v_prefix] = v
                        else:
                            to_remove.add(v)
                    else:
                        children_prefixes[v_prefix] = v
                self.set_children(
                    u,
                    [
                        v
                        for v in self.children(u)
                        if v not in to_remove
                    ]
                )

    def reorder_or_nodes(self, u=None):
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return

        if self.is_unary(u):
            self.reorder_or_nodes(self.first_child(u))

        elif self.is_n_ary(u):
            for v in self.children(u):
                self.reorder_or_nodes(v)
            if self.label(u) == "|":
                self.map_node_children[u] = sorted(
                    self.map_node_children[u],
                    key=lambda v: self.to_prefix_regexp_str(v)
                )

    def find_unary_n_aries(self, u=None):
        if u is None:
            print(self.to_prefix_regexp_list())
            u = self.first_child(self.root)
            if u is None:
                return
        result = set()
        if self.is_unary(u):
            result |= self.find_unary_n_aries(self.first_child(u))

        elif self.is_n_ary(u):
            if len(self.children(u)) == 1:
                result.add(u)
            for v in self.children(u):
                result |= self.find_unary_n_aries(v)
        return result

    def remove_unary_n_aries(self, u=None):
        if u is None:
            u = self.first_child(self.root)
            if u is None:
                return

        if self.is_unary(u):
            self.remove_unary_n_aries(self.first_child(u))

        elif self.is_n_ary(u):
            if len(self.children(u)) == 1:
                u_parent = self.parent(u)
                i = self.get_arc_index(u_parent, u)
                u_child = self.first_child(u)
                self.set_ith_child(u_parent, u_child, i)
                self.remove_node(u)
                self.remove_unary_n_aries(u_child)
            else:
                for v in self.children(u):
                    self.remove_unary_n_aries(v)

    def walk_one_char(self, u: int, a: str, verbose: bool = False) -> set:
        """
        Performs a single character walk on this :py:class:`RegexpAst`
        instance.
        Starts the walk on the node u (u must be a leaf or the root),
        and returns the set of leaves labeled by ``a``
        that are epsilon-reachable from ``u``.

        Args:
            a (str): A symbol, e.g. "a" or "$date".

        Returns:
            The set of leaves that are reached from ``u`` by consuming ``a``.
        """
        result = set()
        v = self.parent(u)  # if u is root, v will be None
        if verbose:
            print("5_____start")
            ipynb_display_graph(self)
            print(u, v)
            print(a)
            print("5______end")
        epsilon_reachables = self.epsilon_reachables(u, v)
        for uu, vv in epsilon_reachables:
            if vv is not None and self.label(vv) == a:
                result.add(vv)
        return result

    def walk_word(self, w: list, u: int = None) -> set:
        """
        Walk on this :py:class:`RegexpAst` instances by consuming the symbols
        involved in an input word.

        Args:
            u (int): The vertex descriptor of the starting node.
                Pass ``None`` to start from the root of this
                :py:class:`RegexpAst` instance. Defaults to ``None``.
            w (list): The input word, which is a list of symbols,
                where each symbol s a string (e.g., ``"a"`` or ``"$date"``).

        Returns:
            The set of leaves that are reached from ``u`` by consuming ``w``.
        """
        if u is None:
            u = self.root
        possible_locations = {u}
        for a in w:
            new_possible_locations = set()
            for leaf in possible_locations:
                new_possible_locations |= self.walk_one_char(leaf, a)
            possible_locations = new_possible_locations
        return possible_locations

    def recognizes(self, x) -> bool:
        return (
            self.recognizes_pa(x) if isinstance(x, PatternAutomaton)
            else self.recognizes_word(x)
        )

    def recognizes_pa(
        self,
        pa: PatternAutomaton,
        verbose: bool = False
    ) -> bool:
        """
        Let :math:`bot` be the root of the AST.

        - With str: is there a path from bot to :math:`\\bot`
          recognizing an arbirary word?
        - With PAs: is there a path from bot to :math:`\\bot`
          recognizing a path from the source to the sink of the PA?
        """
        stack = deque()
        u = self.root
        stack.append((u, 0))
        while stack:
            (u, q) = stack.pop()
            if pa.is_final(q):
                v = self.parent(u)
                if any(
                    vv == self.root
                    for (_, vv) in self.epsilon_reachables(u, v)
                ):
                    return True
                else:
                    continue
            for e in pa.out_edges(q):
                r = pa.target(e)
                p = pa.label(e)
                compatible_leaves = self.walk_one_char(u, p, verbose=verbose)
                for leaf in compatible_leaves:
                    stack.append((leaf, r))
        return False

    def recognizes_pa_prefix(
        self,
        pa: PatternAutomaton,
        target_pa_node: int,
        target_ast_leaf: int,
        u: int = None
    ) -> bool:
        """
        Tests whether there exists in this :py:class:`RegexpAst` instance
        a path from its root to ``target_ast_leaf`` that corresponds to
        a path from the source of a given :py:class:`PatternAutomaton` instance
        to ``target_ast_leaf``.

        Args:
            pa (PatternAutomaton): A :py:class:`PatternAutomaton` instance
                (modeling a positive example).
            target_pa_node (int): The vertex descriptor of the target node
                in ``pa``.
            target_ast_leaf (int): The vertex descriptor target leaf
                in ``self``.
            u (int): Pass ``None``.

        Returns:
             ``True`` iff this :py:class:`RegexpAst` instance matches ``pa``,
            ``False`` otherwise.
        """
        stack = deque()
        if u is None:
            u = self.root
        stack.append((u, 0))
        while stack:
            u, q = stack.pop()
            if u == target_ast_leaf and q == target_pa_node:
                return True
            if q > target_pa_node:
                continue
            for e in pa.out_edges(q):
                r = e.m_target
                p = pa.label(e)
                compatible_leaves = self.walk_one_char(u, p)
                for leaf in compatible_leaves:
                    stack.append((leaf, r))
        return False

    def recognizes_word(self, w: list) -> bool:
        """
        Tests whether a word is matched by this :py:class:`RegexpAst` instance.

        Args:
            w (list): A list of symbols, where each symbol is a string
                (e.g. ``"a"`` or ``"$date"``).

        Returns:
            ``True`` iff this :py:class:`RegexpAst` instance matches ``w``,
            ``False`` otherwise.
        """
        possible_last_leaves = self.walk_word(w)
        return any(
            v == self.root
            for leaf in possible_last_leaves
            for _, v in self.epsilon_reachables(
                leaf, self.map_node_parent[leaf]
            )
        )

    def recognizes_prefix(self, prefix: list, leaf_to_end_on: int):
        """
        Tests whether there exists a valid walk from the root to
        a given leaf in this :py:class:`RegexpAst` instance.

        Args:
            prefix (list): The prefix (list of symbols).
            leaf_to_end_on (int): The vertex descriptor target leaf.

        Returns:
            ``True`` if there exists a walk from the root to
            ``leaf_to_end_on`` that matches ``prefix``, ``False`` otherwise.
        """
        # print("4_____start")
        # ipynb_display_graph(self)
        # print(prefix)
        # print(leaf_to_end_on)
        # print("4______end")
        return leaf_to_end_on in self.walk_word(prefix)

    # --------------------------------------------------------------------------
    # The following methods are reuired to use pybgl.graphviz
    # --------------------------------------------------------------------------

    def edges(self) -> iter:
        """
        Retrieves an iterator over the edges of this :py:class:`RegexpAst`
        instance.

        Returns:
            An iterator over this :py:class:`RegexpAst` instance edges.
        """
        return (
            EdgeDescriptor(u, v, 0)  # TODO: we could just return (u, v)
            for (u, vs) in self.map_node_children.items()
            for v in vs
        )

    def out_edges(self, u: int) -> iter:
        """
        Retrieves an iterator over the out-edges of this :py:class:`RegexpAst`
        instance.

        Returns:
            An iterator over this :py:class:`RegexpAst` instance vertices.
        """
        return self.map_node_children[u]

    def vertices(self) -> iter:
        """
        Retrieves an iterator over the vertices of this :py:class:`RegexpAst`
        instance.

        Returns:
            An iterator over this :py:class:`RegexpAst` instance vertices.
        """
        return self.map_node_children.keys()

    def source(self, e: EdgeDescriptor) -> int:
        """
        Retrieves the source of an arc.

        Args:
            e (EdgeDescriptor): The ``EdgeDescriptor`` of the arc.

        Returns:
            The vertex descriptor of the source of ``e``.
        """
        return e.source

    def target(self, e: EdgeDescriptor) -> int:
        """
        Retrieves the target of an arc.

        Args:
            e (EdgeDescriptor): The ``EdgeDescriptor`` of the arc.

        Returns:
            The vertex descriptor of the target of ``e``.
        """
        return e.target

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`RegexpAst` to Graphviz format.

        Returns:
            The corresponding Graphviz string.
        """
        self.directed = True
        dg = {"rankdir": "TB"}
        dpv = {
            "label": make_func_property_map(
                lambda u: "%s [%s]" % (u, self.map_node_label[u])
            ),
        }
        dv = {
            "shape": "box",
            "style": "rounded, filled",
            "ordering": "out"
        }
        kwargs = enrich_kwargs(dg, "dg", **kwargs)
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(dv, "dv", **kwargs)
        return to_dot(self, **kwargs)


def prefix_regexp_to_ast(prefix_regexp: list) -> RegexpAst:
    """
    Builds a :py:class:`RegexpAst` instance from a prefix
    regular expression.

    Args:
        prefix_regexp (list): A list modeling a binary prefix regular
           expression e.g. [".", "a", "$date"].

    Returns:
        The corresponding :py:class:`RegexpAst` instance.
    """
    ast = RegexpAst()
    stack = deque()
    stack.append((ast.root, 1))
    for regexp_token in prefix_regexp:
        u, child_idx = stack.pop()
        v = ast.add_node(label=regexp_token)
        if child_idx == 1:
            ast.set_child(u, v)
        else:
            ast.append_child(u, v)

        if ast.is_n_ary(v):
            stack.append((v, 2))
            stack.append((v, 1))
        elif ast.is_unary(v):
            stack.append((v, 1))

    assert len(stack) == 0
    ast.simplify()
    return ast
