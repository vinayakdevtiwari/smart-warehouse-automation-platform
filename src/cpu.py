"""
Simulated CPU / Processing Resource for Warehouse Task Execution.

Models a single-core CPU executing processes one time unit at a time,
tracking busy time, idle time, and process state transitions.
"""

from typing import Optional, Tuple
from src.pcb import PCB, ProcessState


class SimulatedCPU:
    """
    Simulated CPU resource.
    """

    def __init__(self):
        self.current_process: Optional[PCB] = None
        self.busy_ticks: int = 0
        self.idle_ticks: int = 0

    def is_idle(self) -> bool:
        """Check whether the CPU is currently idle."""
        return self.current_process is None

    def allocate(self, pcb: PCB, current_time: int) -> None:
        """
        Allocate the CPU to a new process (Context switch / Dispatch).
        Transitions process state to RUNNING.
        """
        self.current_process = pcb
        self.current_process.mark_started(current_time)

    def preempt(self) -> Optional[PCB]:
        """
        Preempt the currently running process and return it to READY state.
        Returns the preempted PCB or None if CPU was idle.
        """
        if self.current_process is None:
            return None
        preempted = self.current_process
        preempted.mark_ready()
        self.current_process = None
        return preempted

    def execute_tick(self, current_time: int) -> Tuple[Optional[PCB], bool]:
        """
        Execute one clock tick on the CPU.
        
        Returns:
            Tuple[Optional[PCB], bool]:
                - pcb: The PCB that ran during this tick (or None if idle)
                - completed: True if the process completed execution during this tick
        """
        if self.current_process is None:
            self.idle_ticks += 1
            return None, False

        self.busy_ticks += 1
        self.current_process.execute_unit()

        if self.current_process.is_completed():
            completed_proc = self.current_process
            completed_proc.mark_completed(current_time + 1)
            self.current_process = None
            return completed_proc, True

        return self.current_process, False

    def reset(self) -> None:
        """Reset CPU state for subsequent simulations."""
        self.current_process = None
        self.busy_ticks = 0
        self.idle_ticks = 0
