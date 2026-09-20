"""
Process Control Block (PCB) and Process State Implementation.

Conforms to Unit 2 OS concepts:
- Process state lifecycle: NEW -> READY -> RUNNING -> TERMINATED
- Process Control Block storing identity, scheduling, and accounting information.
"""

from enum import Enum
from typing import Optional


class ProcessState(Enum):
    """
    Standard Operating System Process States (as per Unit 2 syllabus).
    """
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"


class PCB:
    """
    Process Control Block (PCB) representing a warehouse task as an OS process.
    
    Attributes:
        pid (str): Process Identifier (e.g. 'P1', 'P2')
        task_type (str): Warehouse task description (e.g. 'Urgent Order Processing')
        arrival_time (int): Time when task arrives in the system (AT)
        burst_time (int): Total CPU processing time required (BT)
        priority (int): Scheduling priority (1 = Highest, 2 = Normal, 3 = Routine)
        state (ProcessState): Current execution state
        remaining_burst_time (int): Remaining CPU time needed to complete
        start_time (Optional[int]): Time process first receives CPU allocation
        completion_time (Optional[int]): Time process finishes execution (CT)
        turnaround_time (Optional[int]): Total time from submission to completion (TAT = CT - AT)
        waiting_time (Optional[int]): Total time spent waiting in ready queue (WT = TAT - BT)
        response_time (Optional[int]): Time from arrival to first CPU allocation (RT = First Run - AT)
    """

    def __init__(
        self,
        pid: str,
        task_type: str,
        arrival_time: int,
        burst_time: int,
        priority: int
    ):
        if arrival_time < 0:
            raise ValueError("Arrival time cannot be negative.")
        if burst_time <= 0:
            raise ValueError("Burst time must be greater than zero.")
        if priority <= 0:
            raise ValueError("Priority must be a positive integer (e.g. 1, 2, 3).")

        self.pid: str = pid
        self.task_type: str = task_type
        self.arrival_time: int = arrival_time
        self.burst_time: int = burst_time
        self.priority: int = priority

        self.state: ProcessState = ProcessState.NEW
        self.remaining_burst_time: int = burst_time

        # Accounting / Performance Metrics
        self.start_time: Optional[int] = None
        self.completion_time: Optional[int] = None
        self.turnaround_time: Optional[int] = None
        self.waiting_time: Optional[int] = None
        self.response_time: Optional[int] = None

    def mark_ready(self) -> None:
        """Transition process to READY state."""
        self.state = ProcessState.READY

    def mark_started(self, current_time: int) -> None:
        """Transition process to RUNNING state and record first response time if not already recorded."""
        self.state = ProcessState.RUNNING
        if self.start_time is None:
            self.start_time = current_time
            self.response_time = current_time - self.arrival_time

    def execute_unit(self) -> None:
        """Simulate execution of 1 unit of CPU time."""
        if self.remaining_burst_time > 0:
            self.remaining_burst_time -= 1

    def mark_completed(self, current_time: int) -> None:
        """Transition process to TERMINATED state and calculate final metrics."""
        self.state = ProcessState.TERMINATED
        self.completion_time = current_time
        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time

    def is_completed(self) -> bool:
        """Check if process has completed its full burst requirement."""
        return self.remaining_burst_time == 0

    def reset(self) -> None:
        """Reset PCB state for re-running in alternative scheduling algorithms."""
        self.state = ProcessState.NEW
        self.remaining_burst_time = self.burst_time
        self.start_time = None
        self.completion_time = None
        self.turnaround_time = None
        self.waiting_time = None
        self.response_time = None

    def clone(self) -> "PCB":
        """Create a fresh duplicate of this process."""
        return PCB(
            pid=self.pid,
            task_type=self.task_type,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority
        )

    def to_dict(self) -> dict:
        """Serialize PCB details into a dictionary."""
        return {
            "pid": self.pid,
            "task_type": self.task_type,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "state": self.state.value,
            "remaining_burst_time": self.remaining_burst_time,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time,
            "response_time": self.response_time,
        }

    def __repr__(self) -> str:
        return (
            f"PCB(PID={self.pid}, Type='{self.task_type}', "
            f"AT={self.arrival_time}, BT={self.burst_time}, "
            f"Prio={self.priority}, State={self.state.value}, Rem={self.remaining_burst_time})"
        )
