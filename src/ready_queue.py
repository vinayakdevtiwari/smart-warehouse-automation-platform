"""
Ready Queue Implementation for Priority-Based CPU Scheduling.

Maintains waiting processes ordered by:
1. Priority (lower numerical value = higher priority)
2. FCFS tie-breaking (earlier arrival time, then alphabetical PID)
"""

from typing import List, Optional
from src.pcb import PCB, ProcessState


class ReadyQueue:
    """
    Ready Queue structure holding processes ready for CPU allocation.
    """

    def __init__(self):
        self._queue: List[PCB] = []

    def enqueue(self, pcb: PCB) -> None:
        """
        Add a process to the ready queue and maintain priority ordering.
        Transitions the process state to READY.
        """
        pcb.mark_ready()
        self._queue.append(pcb)
        self._sort_queue()

    def dequeue(self) -> Optional[PCB]:
        """
        Remove and return the highest-priority process from the queue.
        Returns None if queue is empty.
        """
        if self.is_empty():
            return None
        return self._queue.pop(0)

    def peek(self) -> Optional[PCB]:
        """
        View the highest-priority process without removing it.
        Returns None if queue is empty.
        """
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self) -> bool:
        """Check if the ready queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Return the number of processes currently waiting in the ready queue."""
        return len(self._queue)

    def get_all(self) -> List[PCB]:
        """Return a copy of all processes currently in the queue."""
        return list(self._queue)

    def _sort_queue(self) -> None:
        """
        Sort queue using:
        1. priority (ascending: 1 > 2 > 3)
        2. arrival_time (ascending: earlier arrival first, FCFS)
        3. pid (ascending: deterministic tie-breaker)
        """
        self._queue.sort(key=lambda p: (p.priority, p.arrival_time, p.pid))

    def __repr__(self) -> str:
        items = [f"[{p.pid}: Prio={p.priority}, AT={p.arrival_time}, Rem={p.remaining_burst_time}]" for p in self._queue]
        return f"ReadyQueue({', '.join(items) if items else 'EMPTY'})"
