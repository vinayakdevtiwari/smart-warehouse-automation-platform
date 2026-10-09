"""
Performance Metrics Calculation for CPU Scheduling Algorithms.

Computes scheduling performance metrics according to Review 1 scope:
- Completion Time (CT)
- Turnaround Time (TAT = CT - AT)
- Waiting Time (WT = TAT - BT)
- Response Time (RT = First Run Time - AT)
- Average Turnaround Time (Avg TAT)
- Average Waiting Time (Avg WT)
- Average Response Time (Avg RT)
"""

from typing import List, Dict, Any
from src.pcb import PCB


class PerformanceMetrics:
    """
    Computes and formats performance metrics for a completed scheduling run.
    """

    def __init__(self, completed_processes: List[PCB], total_simulation_time: int):
        self.processes: List[PCB] = sorted(completed_processes, key=lambda p: p.pid)
        self.total_time: int = total_simulation_time  # Retained internally for simulation accounting
        self.num_processes: int = len(completed_processes)

        self.avg_tat: float = 0.0
        self.avg_wt: float = 0.0
        self.avg_rt: float = 0.0

        self._compute_averages()

    def _compute_averages(self) -> None:
        """Compute average turnaround time, waiting time, and response time."""
        if self.num_processes == 0:
            return

        total_tat = sum(p.turnaround_time for p in self.processes if p.turnaround_time is not None)
        total_wt = sum(p.waiting_time for p in self.processes if p.waiting_time is not None)
        total_rt = sum(p.response_time for p in self.processes if p.response_time is not None)

        self.avg_tat = total_tat / self.num_processes
        self.avg_wt = total_wt / self.num_processes
        self.avg_rt = total_rt / self.num_processes

    def get_summary(self) -> Dict[str, Any]:
        """Return a structured summary dictionary containing only Review 1 metrics."""
        return {
            "total_processes": self.num_processes,
            "average_turnaround_time": round(self.avg_tat, 2),
            "average_waiting_time": round(self.avg_wt, 2),
            "average_response_time": round(self.avg_rt, 2),
            "process_table": [p.to_dict() for p in self.processes]
        }
