#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import time
from pybgl import ipynb_display_graph

from .cbfs import CBFS
from .find_ast_visitor import FindAstFromStringsDefaultVisitor
from .objective_func import (
    make_additive_objective_func_for_str,
    make_multiplicative_objective_func_for_str,
    make_tuple_based_objective_func_for_str,
    make_normalized_additive_objective_func_for_str,
)
from .pattern_automaton import PatternAutomaton
from .regexp_ast import RegexpAst
from .regexp_mutators import MUTATORS


(OBJ_ADD, OBJ_MULT, OBJ_ADD_NORM, OBJ_TUPLE) = range(4)


def shortness_factor(examples: iter) -> float:
    """
    Computes the normalization factor used to ensure the shortness
    is always in [0, 1].

    Args:
        examples (set): The set of positive samples

    Returns:
        The normalization factor.

    Notes:

    - The default behavior of find_ast is to choose :math:`n = 1`.
      However, using n = 1 makes the shortness equal to the size of
      the inferred AST. As a sequel, the shortness is too prepondarant,
      w.r.t. to the accuracy which is in :math:`[0.0, 1.0]`
      and fAST waste a lot of energy to explore irrelevant ASTs.
      That is why we must normalize the shortness.
    - To do so, we should use
      :math:`n = \\sum_{s \\in S^+}(|s|)` where :math:`S^+` is the
      set of positive examples.
      However, this scaling factor is too aggressive if :math:`|S^+|`
      increases.
    - To circumvent the problem, we use
      :math:`n = max_{s \\in S^+}(|s|)`
      Intuitively, this guarantees that
      :math:`0 <= {shortness}(PTA(\\argmax_{s \\in S^+}(|s|))) <= 1`,
      which means that the ASTs we are searching have most of time a
      scaled shortness below 1. This scaling factor makes the shortness
      insensitive to the number of examples (only to the length
      of the longest example) and comparable with the accuracy.
    """
    n = max(len(example) for example in examples)
    return 1 / (2 * n)


def fast_from_strings(
    examples: list,
    objective_function: callable = None,
    stop_condition: callable = None,
    mutators: list = None,
    visitor: FindAstFromStringsDefaultVisitor = None
) -> list:
    """
    Regular expression inference algorithm.

    Args:
        examples (list): The list of input :py:class:`PatternAutomaton`
            instances corresponding to each positive examples.
        objective_function (callable): The objective function to be
            minimized.
        stop_condition (callable): A
            ``callable(candidate_solutions, elapsed_time) -> bool`` function
            where:

            - candidate_solutions (list): The list of the current
              candidates solutions.
            - time_elapsed (float): The current execution time,
              in seconds.
            - the returned value is ``True`` iff the execution must
              be stopped.

        mutators (list): The list of `Mutator` instances used to update
            the ASTs.

    Returns:
        A list of final solutions, once the queue is empty (dream on),
        or once the stop condition is called (more reasonable).
        A final solution is a tuple `(h, prefix_regexp)`
        where `pref_reg: list` is a prefix regular expression of the solution,
        and `h` is its objective function value.
    """
    if visitor is None:
        visitor = FindAstFromStringsDefaultVisitor()
    if objective_function is None:
        alphabet = set(a for w in examples for a in w)
        alpha = shortness_factor(examples)
        objective_function = make_normalized_additive_objective_func_for_str(
            examples=examples,
            alphabet=alphabet,
            density_factor=(1 - alpha),
            size_factor=alpha
        )
    if stop_condition is None:
        def stop_condition(final_results, time_elapsed):
            return len(final_results) == 1
    if mutators is None:
        mutators = [mutator(MUTATORS) for mutator in MUTATORS]

    def indices_to_depth(i: int, k: int) -> int:
        """
        Converts `(i, k)` pair, where `i` is the index of the word being
        processed and `k` the index of the character being processed
        to the corresponding progression. In CBFS, the progression of an AST
        identifies in which queue it must pushed.

        Args:
            i (int): The index of the current positive example.
            k (int): The index of the current character in the
                positive example being processed.

        Returns:
            The current progression.
        """
        return sum(
            len(example.w) if isinstance(example, PatternAutomaton)
            else len(example)
            for example in examples[:i]
        ) + k

    def next_symbols(example, j: int) -> iter:
        if isinstance(example, PatternAutomaton):
            pa = example
            return (
                (pa.label(e), pa.target(e))
                for e in pa.out_edges(j)
            )
        else:  # str
            sigma = w[j]
            k = j + 1
            return [(sigma, k)]

    # Maximum progression of the problem
    total_depth = sum(
        len(example.w) if isinstance(example, PatternAutomaton)
        else len(example)
        for example in examples
    ) + 1

    # Keep track of the pushed regexps to prevent duplicates
    pushed_regexps = {
        depth: set()
        for depth in range(total_depth)
    }

    def was_already_pushed(
        ast: RegexpAst,
        active_leaf: int,
        push_idx: int
    ) -> bool:
        """
        Checks whether an AST has already been seen. To check this the AST
        is converted to a string identifier and this key is stored in
        `pushed_regexps`.

        Args:
            ast (RegexpAst): The considered AST.
            active_leaf (int): The active leaf of ``ast``.
            push_idx (int): The depth.

        Returns:
            ``True`` if this AST has already been pushed.
        """
        # print(ast.to_prefix_regexp_list())
        # ipynb_display_graph(ast)
        ast_key = '$'.join(ast.to_prefix_regexp_list()), active_leaf
        if ast_key in pushed_regexps[push_idx]:
            return True
        else:
            pushed_regexps[push_idx].add(ast_key)
            return False

    # Cache to keep track of regexps objective_function's value,
    # to prevent redundant computations
    map_regexp_value = dict()

    def compute_objective_value(
        ast: RegexpAst,
        examples: list
    ) -> float:
        """
        Computes the value returned by the objective function
        given a candidate solution and the list of positive examples.

        Args:
            ast (RegexpAst): The candidate solution.
            examples: A list of `PatternAutomaton` instances.

        Returns:
            The corresponding objective function value. The lower
            this value, the better the candidate solution.
        """
        ast_key = '$'.join(ast.to_prefix_regexp_list())
        if ast_key not in map_regexp_value.keys():
            map_regexp_value[ast_key] = objective_function(
                ast, examples
            )
        return map_regexp_value[ast_key]

    # List to store final results (tuples obj_value, ast)
    final_results = []

    # Initialize the CBFS priority queue.
    cbfs_q = CBFS(total_depth)

    # Build the initial item of our pq
    i = 0                       # index of current PA
    k = 0                       # current progression in current string
    ast_counter = 0             # ast counter, acts as distinguisher in the pq
    initial_ast = RegexpAst()   # initial empty ast
    active_leaf = initial_ast.root
    obj_func_value = 0          # any value would do, will never be compared

    initial_pq_item = (
        obj_func_value, ast_counter, initial_ast,
        active_leaf, i, k
    )
    cbfs_q.push(initial_pq_item, indices_to_depth(i, k))
    ast_counter += 1

    # Main loop
    t_start = time()
    while not cbfs_q.is_empty():

        # Check the final condition
        time_elapsed = time() - t_start
        if stop_condition(final_results, time_elapsed):
            # print("stop condition triggered")
            break

        # Get the next item to process from the priority queue
        # print(cbfs_q.queues[cbfs_q.pop_idx])
        pq_item = cbfs_q.pop()
        obj_func_value, _, ast, active_leaf, i, j = pq_item
        print(i, j, "___", ast.to_prefix_regexp_str())
        w = (
            examples[i].w if isinstance(examples[i], PatternAutomaton)
            else examples[i]
        )
        visitor.visit_pop_item(pq_item)

        # If we have reached the end of the current positive example.
        if j == len(w):
            # print("end of word %s" % i)
            # move to next string
            i += 1
            j = 0
            active_leaf = ast.root
            # Check that the AST still recognizes all
            # the words that have been seen so far
            if any(
                not ast.recognizes(example)
                for example in examples[:i]
            ):
                print("bad", ast.to_prefix_regexp_str())
                ipynb_display_graph(ast)
                continue  # 'bad' ast. discard and move on

        # If we have reach the end of the last example, then the AST is a
        # candidate solution.
        if i == len(examples) or all(
            ast.recognizes(example)
            for example in examples
        ):
            print("final", ast.to_prefix_regexp_str(), obj_func_value)
            ipynb_display_graph(ast)
            final_results.append((obj_func_value, ast))
            visitor.visit_final_solution(obj_func_value, ast)
            continue  # final solution checked and stored, move on

        # not end of last example -> consume character and produce children
        active_leaf_parent = ast.map_node_parent[active_leaf]
        epsilon_reachable_arcs = ast.epsilon_reachables(
            active_leaf, active_leaf_parent
        )
        # print("eps reachables: %s" % epsilon_reachable_arcs)
        num_mutants = 0
        example = examples[i]
        for (u, v) in epsilon_reachable_arcs:
            for mutator in mutators:
                for (sigma, k) in next_symbols(example, j):
                    # print("       **", a)
                    new_depth = indices_to_depth(i, k)
                    mutated_asts = mutator.mutate(
                        ast,
                        sigma,
                        u,
                        v,
                        (
                            example.w[:k+1] if isinstance(
                                example, PatternAutomaton
                            ) else w[:k]
                        ),
                        examples[:i],
                        epsilon_reachable_arcs,
                        example
                    )
                    num_mutants += len(mutated_asts)
                    for (new_ast, new_active_leaf) in mutated_asts:
                        new_ast.simplify()
                        if was_already_pushed(
                            new_ast, new_active_leaf, new_depth
                        ):
                            continue
                        new_obj_func_value = compute_objective_value(
                            new_ast, examples
                        )
                        new_pq_item = (
                            new_obj_func_value, ast_counter, new_ast,
                            new_active_leaf, i, k
                        )
                        # print(f"   pushing {new_ast.to_prefix_regexp_str()}")
                        cbfs_q.push(new_pq_item, new_depth)
                        visitor.visit_push_item(
                            mutator, new_depth, new_pq_item
                        )
                        ast_counter += 1
        print(f"     generated {num_mutants} mutants")

    return final_results


def fast(
    examples: list,
    obj_id: int = OBJ_ADD,
    stop_condition: callable = (
        lambda final_results, time_elapsed: len(final_results) == 1
    ),
    mutators: list = MUTATORS,
    *cls, **kwargs
) -> list:
    """
    Runs fAST algorithm to infer regular expression from a set of
    positive examples.

    Args:
        examples (list): A ``set(str)`` gathering the positive examples.
        obj_id (int): A value among ``{OBJ_ADD, OBJ_MULT, OBJ_TUPLE}``.
        stop (callable): Stopping
            ``callable(final_results: list, time_elapsed: float) -> bool``
            callback.
        mutators (list): Defaults to ``MUTATORS``.
        cls, kwargs: See the
            :py:func:`objective_func.make_*_objective_funcfor_str`
            function.

    Returns:
        The found regular expressions.
    """
    alphabet = set(a for w in examples for a in w)
    make_obj = [
        make_additive_objective_func_for_str,
        make_multiplicative_objective_func_for_str,
        make_normalized_additive_objective_func_for_str,
        make_tuple_based_objective_func_for_str
    ][obj_id]

    if obj_id == OBJ_ADD and "size_factor" not in kwargs.keys():
        kwargs["size_factor"] = shortness_factor(examples)

    # TODO: one pattern per letter
    # transform examples to a list of PA
    f_obj = make_obj(
        examples=examples,
        alphabet=alphabet,
        *cls, **kwargs
    )
    return fast_from_strings(
        examples=examples,
        objective_function=f_obj,
        stop_condition=stop_condition,
        mutators=[mutator(mutators) for mutator in mutators]
    )


def fast_from_re(
    regexp: str,
    num_examples: int = 10,
    p_stop_final: float = 0.5,
    repeat: bool = True,
    max_sampling: int = 1000,
    *cls, **kwargs
) -> list:
    """
    Runs fAST algorithm to infer regular expression from a set of
    positive examples.

    Args:
        regexp(str): A regular expression.
        num_examples(int): Number of positive examples.
        p_stop_final (float): A ``float`` between ``0.0`` and ``1.0``
            corresponding the probability to stop when reaching a final
            state of the automaton induced by ``regexp``.
            The higher ``p_stop_final``, the longer the examples.
        repeat(bool): Pass `True` to rerun sampling in case of reject.
        max_sampling (int): Maximum number of sampling. Pass ``None``
            to continue sampling until finding a non-rejected value.
            Note that if `sample` always returns ``None``, this results
            to an infinite loop.
        cls, kwargs: see the :py:func:`fast` function .

    Returns:
        The found regular expressions.
    """
    from pybgl import compile_dfa
    from .random import random_word_from_automaton

    g = compile_dfa(regexp)
    examples = set()
    while len(examples) < num_examples:
        w = random_word_from_automaton(g, p_stop_final, repeat, max_sampling)
        examples.add(w)
    print(examples)

    for kw in ("num_examples", "p_stop_final", "repeat", "max_sampling"):
        kwargs.pop(kw, None)

    solutions = sorted(
        fast(list(examples), *cls, **kwargs),
        key=lambda solution: solution[0],
    )
    return [(score, ast.to_infix_regexp_str()) for (score, ast) in solutions]


def fast_benchmark(
    map_relen_numre: dict = None,
    alphabet: list = None,
    num_examples: int = 10,
    *cls,
    **kwargs
) -> float:
    """
    Tests fAST on a custom benchmark by crafting a set of
    test regular expressions. The goal is to test whether
    fAST finds the original (or a better) regular
    expression.

    Args:
        map_relen_numre (dict): A dictionary which maps for each
            length the number of regular expressions to be randomly crafted.
        alphabet (list): The list of symbols.
        num_examples (int): The number of positive samples to be generated
            for this evaluation.
        cls, kwargs: See the :py:func:`fast` function.
    """
    from pybgl import compile_dfa
    from pprint import pformat
    from .random import random_ast, random_word_from_automaton

    def is_valid(g, examples):
        return all(g.accepts(example) for example in examples)

    if map_relen_numre is None:
        map_relen_numre = {
            re_len: 10
            for re_len in range(5, 20, 5)
        }
    if not alphabet:
        alphabet = list("abcde")
    for kw in ("map_relen_numre", "alphabet"):
        kwargs.pop(kw, None)

    num_tries = 0
    num_successes = 0
    for (re_len, num_regexps) in map_relen_numre.items():
        print("=" * 80)
        print(f"re_len = {re_len}")
        for index_instance in range(num_regexps):
            print("-" * 80)
            # Generate random regexp
            ast = random_ast(re_len, alphabet)
            regexp = ast.to_expr().replace(".", "")
            print(f"input regexp = {regexp}")
            g = compile_dfa(regexp)

            # Generate positive examples
            examples = set()
            i = 0
            while len(examples) < num_examples:
                w = random_word_from_automaton(
                    g, p=0.5, repeat=True, max_sampling=1000
                )
                if w:
                    # TODO: fix fast_from_strings to that is support
                    # the "" example.
                    examples.add(w)
                i += 1
                if i == 100:
                    print(
                        "The target language seems very small, stopping with "
                        f"{len(examples)} instead of {num_examples}"
                    )
                    break
            print(f"examples = {pformat(examples)}")

            # Run fAST inference
            solutions = sorted(
                fast(
                    list(examples),
                    stop_condition=(
                        lambda final_results, time_elapsed: (
                            len(final_results) == 1 or time_elapsed > 10
                        )
                    ),
                    *cls, **kwargs
                ),
                key=lambda solution: solution[0],
            )

            regexps = [
                ast.to_infix_regexp_str().replace(".", "")
                for (score, ast) in solutions
            ]
            print(f"output regexps = {pformat(regexps)}")
            if any(
                is_valid(compile_dfa(regexp), examples)
                for regexp in regexps
            ):
                print("SUCCESS")
                num_successes += 1
            else:
                print("FAIL")
            num_tries += 1

    return (num_successes, num_tries)
