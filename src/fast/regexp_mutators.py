#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import chain, combinations
from typing import List, Tuple
from .pattern_automaton import PatternAutomaton
from .regexp_ast import RegexpAst

# TODO remove mutators_to_bounce_on from each constructor
# TODO transform each class to a function


class Mutator:
    def __init__(self, mutators_to_bounce_on):
        self.name = "Default"

    def mutate(
        self,
        ast: RegexpAst,  # the ast to modify
        sigma,  # character (or pattern) being processed
        u,  # source node of e the epsilon reachable arc
        v,  # target node of e
        prefix_word: list,  # the prefix word being processed
        previous_words: List[list],  # the words already processed
        epsilon_reachables: List[tuple],  # the epsilon reachable arcs
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        return []


class DisjunctionMutator(Mutator):
    """
    Downwards mutator, inserting a new 'or' node and a new leaf labeled c.
    Condition: the arc u, v must go downwards.
    """
    def __init__(self, mutators_to_bounce_on):
        self.name = "DisjunctionMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        if v is None or ast.is_upwards_arc(u, v):
            return []
        # print("6____________start")
        # ipynb_display_graph(ast)
        # print(u, v, c)
        # print("6____________end")
        # print("1 --> %s" % ast.to_prefix_regexp_str())
        new_ast = ast.copy()
        new_or_node = new_ast.add_node(label="|")
        new_leaf = new_ast.add_node(label=c)

        i = new_ast.get_arc_index(u, v)
        new_ast.set_ith_child(u, new_or_node, i)
        new_ast.append_child(new_or_node, v)
        new_ast.append_child(new_or_node, new_leaf)
        # print("6bis____________start")
        # ipynb_display_graph(new_ast)
        # print(new_leaf)
        # print("6bis____________end")
        return [(new_ast, new_leaf)]


class BotMutator(Mutator):
    """
    'Bot' mutator. Is used to add a leaf to an empty tree.
    Condition: the ast is empty.
    """
    def __init__(self, mutators_to_bounce_on):
        self.name = "BotMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        if u != ast.root or v is not None or ast.num_nodes > 1:
            return []
        new_ast = ast.copy()
        new_leaf = new_ast.add_node(label=c)
        new_ast.set_child(u, new_leaf)
        return [(new_ast, new_leaf)]


class ActivateMutator(Mutator):
    """
    'Identity' mutator. Does not modify the ast, only activates
    an existing leaf.
    Condition: v is a c-labeled leaf.
    """
    def __init__(self, mutators_to_bounce_on):
        self.name = "ActivateMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        if v is None or not ast.is_leaf(v) or ast.label(v) != c:
            return []
        else:
            return [(ast, v)]


# Left
class DownDotMutator(Mutator):
    """
    Upwards dot mutator.
    Starts by trying to inject in the ast a dot node as child of u,
    a new leaf as left child of it, and v as its right child.
    If this newly obtained ast does not recognize the prefix word
    being processed now, or does not recognize one of the previous
    examples processed, then we also insert a ? node between the dot and v.
    Condition: the arc u, v must go downwards.
    """
    def __init__(self, mutators_to_bounce_on):
        self.name = "DownDotMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        if v is None or ast.is_upwards_arc(u, v):
            return []
        # print("3____________start")
        # ipynb_display_graph(ast)
        # print(u, v, c)
        # print("3____________end")
        new_ast = ast.copy()
        new_dot_node = new_ast.add_node(label=".")
        new_leaf = new_ast.add_node(label=c)
        new_question_node = new_ast.add_node(label="?")

        i = new_ast.get_arc_index(u, v)
        new_ast.set_ith_child(u, new_dot_node, i)
        new_ast.append_child(new_dot_node, new_question_node)
        new_ast.append_child(new_dot_node, v)
        new_ast.set_child(new_question_node, new_leaf)
        return [(new_ast, new_leaf)]

        # new_ast.append_child(new_dot_node, v)
        # print("3bis____________start")
        # ipynb_display_graph(new_ast)
        # print(new_leaf)
        # print("3bis____________end")
        # if new_ast.recognizes_pa_prefix(
        #     current_pa,
        #     target_pa_node=len(prefix_word),
        #     target_ast_leaf=new_leaf
        # ):
        #
        #     if all(
        #             new_ast.recognizes_pa(pa) for pa in previous_words
        #     ):  # case where all works without the '?'

        # # case where we need to '?' the subtree rooted in v
        # new_question_node = new_ast.add_node(label="?")
        # j = new_ast.get_arc_index(new_dot_node, v)  # -> should always be 1
        # new_ast.set_ith_child(new_dot_node, new_question_node, j)
        # new_ast.set_child(new_question_node, v)

        # return [(new_ast, new_leaf)]


# Right
class UpDotMutator(Mutator):
    """
    Upwards dot mutator.
    Starts by trying to inject in the ast a dot node and a leaf as right child.
    If this newly obtained ast does not recognize the prefix word
    being processed now, or does not recognize one of the previous
    examples processed, then we also insert a ? node between the dot and
    the leaf
    Condition: the arc u, v must go upwards.
    """
    def __init__(self, mutators_to_bounce_on):
        self.name = "UpDotMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        if v is None or ast.is_downwards_arc(u, v):
            return []
        # print("9____________start")
        # ipynb_display_graph(ast)
        # print(u, v, c)
        # print("9____________end")

        new_ast = ast.copy()
        new_dot_node = new_ast.add_node(label=".")
        new_leaf = new_ast.add_node(label=c)

        # Inserts "." in the middle of the upward arc (v, u) and the new leaf
        i = new_ast.get_arc_index(v, u)
        new_ast.set_ith_child(v, new_dot_node, i)
        new_ast.append_child(new_dot_node, u)
        new_ast.append_child(new_dot_node, new_leaf)
        # print("9bis____________start")
        # ipynb_display_graph(new_ast)
        # print(new_leaf)
        # print("9bis____________end")
        if (
            (
                isinstance(current_pa, str)
                and new_ast.recognizes_prefix(
                    prefix_word,
                    new_leaf
                )
            ) or (
                isinstance(current_pa, PatternAutomaton)
                and new_ast.recognizes_pa_prefix(
                    current_pa,
                    target_pa_node=len(prefix_word) - 1,
                    target_ast_leaf=new_leaf
                )
            )
        ):
            # If the example is "abcd" and the current character is "c", then
            # the target_pa node is "c" and the prefix to recognize is "abc".
            # MANDO: there is a bug here. For example if
            # S = {"abc", "abcabc", "abcabcabc"}, there is a ? node on top of
            # the "c" leaf.
            # MAX: the bug could be in target_pa_node (check indices) or
            # in recognizes_pa_prefix. Hopefully this is the first reason.
            if all(
                new_ast.recognizes(w)
                for w in previous_words
            ):  # case where all works without the '?'
                return [(new_ast, new_leaf)]

        # case where we need to '?' the new leaf
        new_question_node = new_ast.add_node(label="?")
        j = new_ast.get_arc_index(new_dot_node, new_leaf)  # should always be 1
        new_ast.set_ith_child(new_dot_node, new_question_node, j)
        new_ast.set_child(new_question_node, new_leaf)
        return [(new_ast, new_leaf)]


NON_BOUCING_MUTATORS = [
    DisjunctionMutator,
    BotMutator,
    ActivateMutator,
    UpDotMutator,
    DownDotMutator,
]

MUTATORS_TO_BOUNCE_ON = NON_BOUCING_MUTATORS


class BouncePlusMutator(Mutator):
    """
    'Bouncer' mutator.
    Starts by applying a first mutation on e (insertion of +).
    Then generates from this mutation a new set of Epsilon reachable arc
    on which the non bouncing mutators can be applied.
    TODO: Find out if/how the bouncers can call each other
    Condition: u, v is an upwards arc,
    and v, u is not epsilon-reachable from the current leaf.
    """
    def __init__(self, mutators_to_bounce_on):
        self.mutators_to_bounce_on = mutators_to_bounce_on
        self.name = "BouncePlusMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        result = []
        if v is None \
           or ast.is_downwards_arc(u, v) \
           or (v, u) in epsilon_reachables:
            return result

        asts_to_bounce_on = []
        # print("1______start")
        # print(ast.to_prefix_regexp_str())
        # ipynb_display_graph(ast)
        # print(u, v)
        # print(epsilon_reachables)
        # print("1______end")
        # In any case, we simply introduce a '+' between u & v
        new_ast = ast.copy()
        new_plus_node = new_ast.add_node(label="+")
        new_ast.set_ith_child(v, new_plus_node, new_ast.get_arc_index(v, u))
        # new_ast.map_node_children[v][new_ast.get_arc_index(v, u)] = new_plus_node
        new_ast.set_child(new_plus_node, u)
        # create a 'local' epsilon_reachables specific to this new ast
        # and takes in account the modification done on it
        local_eps_reachables = epsilon_reachables.copy()
        local_eps_reachables |= {
            (new_plus_node, v), (u, new_plus_node)
        }
        local_eps_reachables.remove((u, v))
        new_eps_reachables = new_ast.epsilon_reachables(
            new_plus_node, u
        )
        newly_eps_reachables = new_eps_reachables - local_eps_reachables
        all_epsilon_reachables = new_eps_reachables | local_eps_reachables
        # print("1bis______start")
        # print(new_ast.to_prefix_regexp_str())
        # ipynb_display_graph(new_ast)
        # print(new_plus_node, v)
        # print(local_eps_reachables)
        # print("1bis______end")
        asts_to_bounce_on.append((
            new_ast, all_epsilon_reachables, newly_eps_reachables
        ))

        if ast.is_n_ary(v) and ast.label(v) == ".":
            # in this case, there are several possibilities to insert a + node
            # with u the ith child, we put the range j-k of v's children below
            # the +, with j <= i <= k
            i = ast.get_arc_index(v, u)
            for j in range(i):
                # remove the case where all children would have to move
                # as it will be handled when processing the arc (v, p_v)
                if i == ast.num_children(v) and j == 0:
                    continue
                new_ast = ast.copy()
                new_plus_node = new_ast.add_node(label="+")
                new_dot_node = new_ast.add_node(label=".")
                v_children = new_ast.children(v)
                new_ast.set_children(
                    v,
                    v_children[:j] + [new_plus_node] + v_children[i+1:]
                )
                new_ast.set_child(new_plus_node, new_dot_node)
                new_ast.set_children(
                    new_dot_node,
                    v_children[j: i+1]
                )
                # create a 'local' epsilon_reachables specific to this new ast
                # and takes in account the modification done on it
                local_eps_reachables = epsilon_reachables.copy()
                # since (u, v) was in eps reachables, so are (u, new_dot_node)
                # (new_dot_node, new_plus_node) and (new_plus_node, v)
                local_eps_reachables.remove((u, v))
                local_eps_reachables |= {
                    (u, new_dot_node),
                    (new_dot_node, new_plus_node),
                    (new_plus_node, v)
                }
                # we now 'repair' the eps reachables arcs
                # which have been modified
                for v_child in v_children[j: i+1]:
                    if (v_child, v) in local_eps_reachables:
                        local_eps_reachables.remove((v_child, v))
                        local_eps_reachables.add((v_child, new_dot_node))
                    if (v, v_child) in local_eps_reachables:
                        local_eps_reachables.remove((v, v_child))
                        local_eps_reachables.add((new_dot_node, v_child))
                # finally, we add the reachable arcs that can be accessed
                # using the plus node we just added
                new_eps_reachables = new_ast.epsilon_reachables(
                    new_plus_node, new_dot_node
                )
                newly_eps_reachables = new_eps_reachables - local_eps_reachables
                all_epsilon_reachables = new_eps_reachables | local_eps_reachables
                # and add this couple for further bouncing
                asts_to_bounce_on += [
                    (new_ast, all_epsilon_reachables, newly_eps_reachables)
                ]

        if ast.is_n_ary(v) and ast.label(v) == "|":
            # in this case, there are several possibilities to insert a + node
            # we can put any combination of v's child containing u below
            # the new + node
            # we need at least one child leaving,
            # and at most all but one child leaving
            # the case 0 children leaving is processed above
            # the case all children leaving is processed when handling (v, p_v)

            i = ast.get_arc_index(v, u)
            others = ast.children(v)[:i] + ast.children(v)[i+1:]
            # print("13_____start")
            # ipynb_display_graph(ast)
            for child_combi in chain.from_iterable(
                combinations(others, num_others)
                for num_others in range(1, len(others))
            ):
                new_ast = ast.copy()
                new_plus_node = new_ast.add_node(label="+")
                new_or_node = new_ast.add_node(label="|")
                children_leaving = list(child_combi) + [u]
                children_staying = [
                    child for child in new_ast.children(v)
                    if child not in children_leaving
                ]
                # print(children_leaving)
                # print(children_staying)
                # should never happen, but better safe than sorry
                if len(children_staying) == 0:
                    continue
                new_ast.set_children(v, children_staying + [new_plus_node])
                new_ast.set_child(new_plus_node, new_or_node)
                new_ast.set_children(new_or_node, children_leaving)
                # ipynb_display_graph(new_ast)
                # create a 'local' epsilon_reachables specific to this new ast
                # and takes in account the modification done on it
                local_eps_reachables = epsilon_reachables.copy()
                # since (u, v) was in eps reachables, so are (new_plus_node, v)
                # and (u, new_plus_node)
                local_eps_reachables.remove((u, v))
                local_eps_reachables |= {
                    (u, new_or_node),
                    (new_or_node, new_plus_node),
                    (new_plus_node, v)
                }
                # we now 'repair' the eps reachables arcs
                # which have been modified
                for v_child in children_leaving:
                    if (v_child, v) in local_eps_reachables:
                        local_eps_reachables.remove((v_child, v))
                        local_eps_reachables.add((v_child, new_or_node))
                    if (v, v_child) in local_eps_reachables:
                        local_eps_reachables.remove((v, v_child))
                        local_eps_reachables.add((new_or_node, v_child))
                # finally, we add the reachable arcs that can be accessed
                # using the plus node we just added
                new_eps_reachables = new_ast.epsilon_reachables(
                    new_plus_node, new_or_node
                )
                newly_eps_reachables = new_eps_reachables - local_eps_reachables
                all_epsilon_reachables = new_eps_reachables | local_eps_reachables
                # and add this couple for further bouncing
                # print(epsilon_reachables)
                # print(local_eps_reachables)
                # print(new_eps_reachables)
                # print(all_epsilon_reachables)
                # print(new_eps_reachables)
                asts_to_bounce_on += [
                    (new_ast, all_epsilon_reachables, newly_eps_reachables)
                ]

        for new_ast, all_epsilon_reachables, newly_eps_reachables in asts_to_bounce_on:
            for uu, vv in newly_eps_reachables:
                for mutator in self.mutators_to_bounce_on:
                    # print("11_____start")
                    if (uu, vv) not in all_epsilon_reachables:
                        # print("ouch2")
                        pass
                    # ipynb_display_graph(new_ast)
                    # print(uu, vv)
                    # print(all_epsilon_reachables)
                    # print(newly_eps_reachables)
                    result += mutator(self.mutators_to_bounce_on).mutate(
                        new_ast,
                        c,
                        uu,
                        vv,
                        prefix_word,
                        previous_words,
                        all_epsilon_reachables,
                        current_pa,
                    )
                    # print("11_____end")
        return result


class BounceQuestionMutator(Mutator):
    """
    'Bouncer' mutator.
    Starts by applying a first mutation on e (insertion of ?).
    Then generates from this mutation a new set of Epsilon reachable arc
    on which the non bouncing mutators can be applied.
    TODO: Find out if/how the bouncers can call each other
    Condition: u, v is an downwards arc,
    and v, u is not epsilon-reachable from the current leaf.
    """
    def __init__(self, mutators_to_bounce_on):
        """
        Constructor.
        """
        self.mutators_to_bounce_on = mutators_to_bounce_on
        self.name = "BounceQuestionMutator"

    def mutate(
        self,
        ast: RegexpAst,
        c,
        u,
        v,
        prefix_word: list,
        previous_words: List[list],
        epsilon_reachables: List[tuple],
        current_pa,
    ) -> List[Tuple[RegexpAst, int]]:
        """
        Mutation related to the '?' operator.
        """
        result = []
        if v is None \
           or ast.is_upwards_arc(u, v) \
           or (v, u) in epsilon_reachables:
            return result
        # print("2______start")
        # print(ast.to_prefix_regexp_str())
        # ipynb_display_graph(ast)
        # print(u, v)
        # print(epsilon_reachables)
        # print("2______end")
        asts_to_bounce_on = []
        # In any case, we simply introduce a '?' between u & v
        new_ast = ast.copy()
        new_question_node = new_ast.add_node(label="?")
        new_ast.set_ith_child(
            u,
            new_question_node,
            new_ast.get_arc_index(u, v)
        )
        # new_ast.map_node_children[u][new_ast.get_arc_index(u, v)] = new_question_node
        new_ast.set_child(new_question_node, v)
        # create a 'local' epsilon_reachables specific to this new ast
        # and takes in account the modification done on it
        local_eps_reachables = epsilon_reachables.copy()
        local_eps_reachables |= {
            (u, new_question_node), (new_question_node, v)
        }
        local_eps_reachables.remove((u, v))
        new_eps_reachables = new_ast.epsilon_reachables(
            new_question_node, u
        )
        newly_eps_reachables = new_eps_reachables - local_eps_reachables
        all_epsilon_reachables = new_eps_reachables | local_eps_reachables
        # print("2bis______start")
        # print(new_ast.to_prefix_regexp_str())
        # ipynb_display_graph(new_ast)
        # print(new_question_node, u)
        # print(local_eps_reachables)
        # print("2bis______end")
        asts_to_bounce_on.append((
            new_ast, all_epsilon_reachables, newly_eps_reachables
        ))

        if ast.is_n_ary(u) and ast.label(u) == ".":
            i = ast.get_arc_index(u, v)
            for j in range(i+1, ast.num_children(u)):
                # remove the case where all children would have to move
                # as it will be handled when processing the arc (v, p_v)
                if i == 0 and j == ast.num_children(u) - 1:
                    continue
                new_ast = ast.copy()
                new_question_node = new_ast.add_node(label="?")
                new_dot_node = new_ast.add_node(label=".")
                u_children = new_ast.children(u)
                new_ast.set_children(
                    u,
                    u_children[:i] + [new_question_node] + u_children[j+1:]
                )
                new_ast.set_child(new_question_node, new_dot_node)
                new_ast.set_children(
                    new_dot_node,
                    u_children[i: j+1]
                )
                # create a 'local' epsilon_reachables specific to this new ast
                # and takes in account the modification done on it
                local_eps_reachables = epsilon_reachables.copy()
                # since (u, v) was in eps reachables, so are (u, new_dot_node)
                # (new_dot_node, new_plus_node) and (new_plus_node, v)
                local_eps_reachables.remove((u, v))
                local_eps_reachables |= {
                    (u, new_question_node),
                    (new_question_node, new_dot_node),
                    (new_dot_node, v)
                }
                # we now 'repair' the eps reachables arcs
                # which have been modified
                for u_child in u_children[i: j+1]:
                    if (u, u_child) in local_eps_reachables:
                        local_eps_reachables.remove((u, u_child))
                        local_eps_reachables.add((new_dot_node, u_child))
                    if (u_child, u) in local_eps_reachables:
                        local_eps_reachables.remove((u_child, u))
                        local_eps_reachables.add((u_child, new_dot_node))
                # finally, we add the reachable arcs that can be accessed
                # using the plus node we just added
                new_eps_reachables = new_ast.epsilon_reachables(
                    new_question_node, u
                )
                all_epsilon_reachables = new_eps_reachables | local_eps_reachables
                newly_eps_reachables = new_eps_reachables - local_eps_reachables
                # and add this couple for further bouncing
                asts_to_bounce_on += [
                    (new_ast, all_epsilon_reachables, newly_eps_reachables)
                ]

        if ast.is_n_ary(u) and ast.label(u) == "|":
            i = ast.get_arc_index(u, v)
            others = ast.children(u)[:i] + ast.children(u)[i+1:]
            # print("12_____start")
            # ipynb_display_graph(ast)
            for child_combi in chain.from_iterable(
                    combinations(others, num_others)
                    for num_others in range(1, len(others))
            ):
                new_ast = ast.copy()
                new_question_node = new_ast.add_node(label="?")
                new_or_node = new_ast.add_node(label="|")
                children_leaving = list(child_combi) + [v]
                children_staying = [
                    child for child in new_ast.children(u)
                    if child not in children_leaving
                ]
                # print(children_leaving)
                # print(children_staying)
                # should never happen, but better safe than sorry
                if len(children_staying) == 0:
                    continue
                new_ast.set_children(u, children_staying + [new_question_node])
                new_ast.set_child(new_question_node, new_or_node)
                new_ast.set_children(new_or_node, children_leaving)
                # ipynb_display_graph(new_ast)
                # create a 'local' epsilon_reachables specific to this new ast
                # and takes in account the modification done on it
                local_eps_reachables = epsilon_reachables.copy()
                # since (u, v) was in eps reachables, so are (new_plus_node, v)
                # and (u, new_plus_node)
                local_eps_reachables.remove((u, v))
                local_eps_reachables |= {
                    (u, new_question_node),
                    (new_question_node, new_or_node),
                    (new_or_node, v)
                }
                # we now 'repair' the eps reachables arcs
                # which have been modified
                for u_child in children_leaving:
                    if (u, u_child) in local_eps_reachables:
                        local_eps_reachables.remove((u, u_child))
                        local_eps_reachables.add((new_or_node, u_child))
                    if (u_child, u) in local_eps_reachables:
                        local_eps_reachables.remove((u_child, u))
                        local_eps_reachables.add((u_child, new_or_node))
                # finally, we add the reachable arcs that can be accessed
                # using the plus node we just added
                new_eps_reachables = new_ast.epsilon_reachables(
                    new_question_node, u
                )
                newly_eps_reachables = new_eps_reachables - local_eps_reachables
                all_epsilon_reachables = new_eps_reachables | local_eps_reachables
                # and add this couple for further bouncing
                # print(epsilon_reachables)
                # print(local_eps_reachables)
                # print(new_eps_reachables)
                # print(all_epsilon_reachables)
                # print(new_eps_reachables)
                asts_to_bounce_on += [
                    (new_ast, all_epsilon_reachables, newly_eps_reachables)
                ]
            # print("12_____end")
        for (
            new_ast, all_epsilon_reachables, newly_eps_reachables
        ) in asts_to_bounce_on:
            for uu, vv in newly_eps_reachables:
                if (uu, vv) not in all_epsilon_reachables:
                    # print("ouch1")
                    pass
                # print("10_____start")
                # ipynb_display_graph(new_ast)
                # print(uu, vv)
                # print(all_epsilon_reachables)
                # print(newly_eps_reachables)
                for mutator in self.mutators_to_bounce_on:
                    result += mutator(self.mutators_to_bounce_on).mutate(
                        new_ast,
                        c,
                        uu,
                        vv,
                        prefix_word,
                        previous_words,
                        all_epsilon_reachables,
                        current_pa,
                    )
                # print("10_____end")
        return result


BOUNCING_MUTATORS = [
    BouncePlusMutator,
    BounceQuestionMutator
]

MUTATORS = NON_BOUCING_MUTATORS + BOUNCING_MUTATORS
