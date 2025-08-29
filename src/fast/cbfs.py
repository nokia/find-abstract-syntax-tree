#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import heapq as hq


class CBFS:
    """
    Implements the `CBFS algorithm
    <https://www.researchgate.net/publication/315650019_Cyclic_best_first_search_Using_contours_to_guide_branch-and-bound_algorithms_Cyclic_Best_First_Search>`__.
    """
    def __init__(self, num_queues: int, pop_idx: int = 0):
        """
        Constructor.

        Args:
            num_queues (int): A strictly positive ``int`` specifying the
                number of queues managed by this :py:class:`CBFS` instance.
            pop_idx (int): The index of the active queue.
                It must verify ``0 <= pop_idx < self.num_queues``.
        """
        self.queues = [
            [] for _ in range(num_queues)
        ]
        for q in self.queues:
            hq.heapify(q)
        self.num_queues = num_queues
        # The number of queues managed by this CBFS instance.
        self.pop_idx = pop_idx
        # The active the CBFS queue.
        self.num_popped = 0
        # The number of popped item from the active CBFS queue
        # in the current cycle.
        self.num_to_pop = 1
        # The number of items to pop from a queue for each cycle.
        self.num_items = 0
        # The number of items stored in the CBFS queues.

    def pop(self) -> object:
        """
        Pops an item from this :py:class:`CBFS` instance.

        Returns:
            The popped item.
        """
        if self.num_items == 0:
            raise RuntimeError("Error (CBFS) cannot pop from an empty queue!")
        if self.num_popped == self.num_to_pop:
            self.pop_idx = (self.pop_idx + 1) % self.num_queues
            self.num_popped = 0
        while len(self.queues[self.pop_idx]) == 0:
            self.pop_idx = (self.pop_idx + 1) % self.num_queues
            self.num_popped = 0

        result = hq.heappop(self.queues[self.pop_idx])
        self.num_popped += 1
        self.num_items -= 1  # TODO if self.num_items > 0:
        return result

    def push(self, item: object, push_idx: int):
        """
        Pushes a new item to this :py:class:`CBFS` instance.

        Args:
            item (object): The item to be pushed
            push_idx (int): The queue index where the item must be pushed.
                It must verifies ``0 <= push_idx < self.num_queues``.
        """
        hq.heappush(self.queues[push_idx], item)
        self.num_items += 1

    def is_empty(self) -> bool:
        """
        Checks whether this :py:class:`CBFS` instance contains
        at least one item.

        Returns:
            ``True`` if this :py:class:`CBFS` as no item,
            ``False`` otherwise.
        """
        return self.num_items <= 0  # TODO == 0
