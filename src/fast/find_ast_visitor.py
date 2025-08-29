#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import time
from .regexp_ast import RegexpAst
from .regexp_mutators import Mutator


# TODO remove visit_ suffix from method names
class FindAstFromStringsDefaultVisitor:
    def __init__(self):
        """
        Constructor.
        """
        pass

    def visit_init_sample(self, examples: list):
        """
        Triggered when starting the fAST inference.

        Args:
            examples (list): The positive examples.
        """
        pass

    def visit_pop_item(self, pq_item: tuple):
        """
        Triggered when processing a mutant.

        Args:
            pq_item: The popped mutant.
        """
        pass

    # TODO simplify some signature
    def visit_push_item(
        self,
        mutator: Mutator,
        new_depth: int,
        new_pq_item: tuple
    ):
        """
        Triggered when building a new mutant.

        Args:
            mutator (Mutator):  The mutator that has produced the mutant.
            new_depth (int): The progression of the item (total number of
                processed characters).
            new_pq_item (tuple): The pushed mutant.
        """
        pass

    def visit_end_sample(self):
        """
        Triggered when a positive example is totally processed.
        """
        pass

    def visit_final_solution(self, obj_func_value: float, ast: RegexpAst):
        """
        Triggered when a candidate solution is found.

        Args:
            obj_func_value (float): The objective function of the
                candidate solution.
            ast (RegexpAst): The candidate solution.
        """
        pass


# TODO To be replaced by pybgl.aggregated_visitor
class FindAstFromStringsAggregateVisitor(FindAstFromStringsDefaultVisitor):
    def __init__(self, visitors: list):
        """
        Constructor.

        Args:
            visitors (list): A list of
                :py:class:`FindAstFromStringsDefaultVisitor` instances.
        """
        self.visitors = visitors

    def visit_init_sample(self, examples):
        """
        Triggered when starting the fAST inference.

        Args:
            examples (list): The positive examples.
        """
        for visitor in self.visitors:
            visitor.visit_init_sample(examples)

    def visit_pop_item(self, pq_item):
        """
        Triggered when processing a mutant.

        Args:
            pq_item: The popped mutant.
        """
        for visitor in self.visitors:
            visitor.visit_pop_item(pq_item)

    def visit_push_item(
        self,
        mutator: Mutator,
        new_depth: int,
        new_pq_item: tuple
    ):
        """
        Triggered when building a new mutant.

        Args:
            mutator (Mutator):  The mutator that has produced the mutant.
            new_depth (int): The progression of the item (total number of
                processed characters).
            new_pq_item (tuple): The pushed mutant.
        """

        for visitor in self.visitors:
            visitor.visit_push_item(mutator, new_depth, new_pq_item)

    def visit_end_sample(self):
        """
        Triggered when a positive example is totally processed.
        """
        for visitor in self.visitors:
            visitor.visit_end_sample()

    def visit_final_solution(self, obj_func_value, ast: RegexpAst):
        """
        Triggered when a candidate solution is found.

        Args:
            obj_func_value (float): The objective function of the
                candidate solution.
            ast (RegexpAst): The candidate solution.
        """
        for visitor in self.visitors:
            visitor.visit_final_solution(obj_func_value, ast)


# TODO: FromStrings -> FromPas
# TODO: DebugVisitor
class FindAstFromStringsVerboseVisitor(FindAstFromStringsDefaultVisitor):
    """
    Insert useful debug message.
    """
    def __init__(self, verbose_level=1):
        self.verbose_level = verbose_level

    def visit_init_sample(self, examples):
        """
        Triggered when starting the fAST inference.

        Args:
            examples (list): The positive examples.
        """
        self.num_pops = 0
        self.time_start = time()

    def visit_pop_item(self, pq_item: tuple):
        """
        Triggered when processing a mutant.

        Args:
            pq_item: The popped mutant.
        """
        self.num_pops += 1
        time_elapsed = time() - self.time_start
        if self.verbose_level >= 1 and self.num_pops % 100 == 0:
            print(
                "    [%5d pops (%4.4f pops/s)]" % (
                    self.num_pops,
                    self.num_pops/time_elapsed,
                )
            )
        if self.verbose_level > 1:
            obj_func_value, _, ast, active_leaf, i, k = pq_item
            print(
                "popping %12s, %2d, %2d - %s" % (
                    ast.to_prefix_regexp_str(),
                    i,
                    k,
                    obj_func_value
                )
            )

    def visit_push_item(self, mutator: Mutator, new_depth: int, new_pq_item):
        """
        Triggered when a positive example is totally processed.
        """
        if self.verbose_level > 2:
            print("        With mutator %s:" % mutator.name)
            obj_func_value, _, ast, active_leaf, i, k = new_pq_item
            print(
                "        pushing %12s, %2d, %2d - %s" % (
                    ast.to_prefix_regexp_str(),
                    i,
                    k,
                    obj_func_value
                )
            )

    def visit_final_solution(self, obj_func_value, ast: RegexpAst):
        """
        Triggered when a candidate solution is found.

        Args:
            obj_func_value (float): The objective function of the
                candidate solution.
            ast (RegexpAst): The candidate solution.
        """
        print(
            "****  Final solution: %s with obj func value of %s  ****" % (
                ast.to_prefix_regexp_str(), obj_func_value
            )
        )


class FindAstFromStringsEvaluateVisitor(FindAstFromStringsDefaultVisitor):
    """
    Maintains metrics when running experiments
    """
    def __init__(self):
        """
        Constructor.
        """
        self.results = []

    def visit_init_sample(self, examples):
        """
        Triggered when starting the fAST inference.

        Args:
            examples (list): The positive examples.
        """
        self.examples = examples

        self.time_start = time()
        self.num_pops = 0
        self.num_pushs = 0
        self.current_results = []

    def visit_pop_item(self, pq_item):
        """
        Triggered when processing a mutant.

        Args:
            pq_item: The popped mutant.
        """
        self.num_pops += 1

    def visit_push_item(
        self,
        mutator: Mutator,
        new_depth: int,
        new_pq_item: tuple
    ):
        """
        Triggered when building a new mutant.

        Args:
            mutator (Mutator):  The mutator that has produced the mutant.
            new_depth (int): The progression of the item (total number of
                processed characters).
            new_pq_item (tuple): The pushed mutant.
        """
        self.num_pushs += 1

    def visit_end_sample(self):
        """
        Triggered when a positive example is totally processed.
        """
        self.results.append((
            self.current_results,
            self.num_pops,
            self.num_pushs,
        ))

    def visit_final_solution(self, obj_func_value, ast: RegexpAst):
        """
        Triggered when a candidate solution is found.

        Args:
            obj_func_value (float): The objective function of the
                candidate solution.
            ast (RegexpAst): The candidate solution.
        """
        time_elapsed = time() - self.time_start
        self.current_results.append((
            obj_func_value,
            ast,
            time_elapsed
        ))
