"""
CPU Schedulers: Non-Preemptive and Preemptive Priority Scheduling.

Implements Unit 2 CPU Scheduling algorithms applied to warehouse process tasks:
1. Non-Preemptive Priority Scheduler: A process retains the CPU until completion.
2. Preemptive Priority Scheduler: A running process is preempted whenever a process with
   strictly higher priority (lower numeric value) enters the Ready Queue.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from src.pcb import PCB, ProcessState
from src.ready_queue import ReadyQueue
from src.cpu import SimulatedCPU


class BaseScheduler(ABC):
    """
    Abstract base class for warehouse process schedulers.
    """

    def __init__(self, processes: List[PCB]):
        # Store clean copies of input processes to avoid mutating external references
        self.processes: List[PCB] = [p.clone() for p in processes]
        self.ready_queue: ReadyQueue = ReadyQueue()
        self.cpu: SimulatedCPU = SimulatedCPU()
        self.current_time: int = 0
        self.timeline: List[Tuple[int, int, Optional[str]]] = []  # (start, end, pid_or_None)
        self.events: List[str] = []
        self.completed_processes: List[PCB] = []

    def _log_event(self, message: str) -> None:
        """Log a chronological simulation event."""
        self.events.append(f"[T={self.current_time}] {message}")

    def _compress_timeline(self, raw_ticks: List[Tuple[int, Optional[str]]]) -> List[Tuple[int, int, Optional[str]]]:
        """
        Compress contiguous 1-tick slices into continuous intervals:
        [(0, 'P1'), (1, 'P1'), (2, 'P2')] -> [(0, 2, 'P1'), (2, 3, 'P2')]
        """
        if not raw_ticks:
            return []

        compressed: List[Tuple[int, int, Optional[str]]] = []
        start_time, current_pid = raw_ticks[0]
        duration = 1

        for t, pid in raw_ticks[1:]:
            if pid == current_pid:
                duration += 1
            else:
                compressed.append((start_time, start_time + duration, current_pid))
                start_time = t
                current_pid = pid
                duration = 1

        compressed.append((start_time, start_time + duration, current_pid))
        return compressed

    @abstractmethod
    def run(self) -> List[PCB]:
        """Run the scheduling simulation and return completed PCB list with metrics."""
        pass


class NonPreemptivePriorityScheduler(BaseScheduler):
    """
    Non-Preemptive Priority CPU Scheduler.
    
    Once the CPU is assigned to a process, it cannot be preempted until its
    CPU burst completes. Incoming processes with higher priority wait at the
    head of the Ready Queue for the next scheduling dispatch.
    """

    def run(self) -> List[PCB]:
        # Sort pending admissions by arrival time, then priority, then PID
        unadmitted: List[PCB] = sorted(
            self.processes,
            key=lambda p: (p.arrival_time, p.priority, p.pid)
        )
        total_processes = len(unadmitted)
        self.current_time = 0
        raw_ticks: List[Tuple[int, Optional[str]]] = []

        self._log_event("Simulation started: Non-Preemptive Priority Scheduling")

        while len(self.completed_processes) < total_processes:
            # 1. Admit any processes that have arrived at or before current_time
            just_arrived = [p for p in unadmitted if p.arrival_time <= self.current_time]
            for p in just_arrived:
                self.ready_queue.enqueue(p)
                unadmitted.remove(p)
                self._log_event(f"ARRIVAL: {p.pid} ('{p.task_type}', Prio={p.priority}, BT={p.burst_time}) entered Ready Queue")

            # 2. If CPU is idle, dispatch next highest priority process
            if self.cpu.is_idle():
                if not self.ready_queue.is_empty():
                    next_process = self.ready_queue.dequeue()
                    self.cpu.allocate(next_process, self.current_time)
                    self._log_event(f"DISPATCH: CPU allocated to {next_process.pid} (Priority {next_process.priority})")
                else:
                    # No processes ready; CPU is idle
                    raw_ticks.append((self.current_time, None))
                    self._log_event("CPU IDLE: No ready processes in queue")
                    self.current_time += 1
                    continue

            # 3. Non-preemptive: Run current process for 1 tick
            running_pid = self.cpu.current_process.pid
            raw_ticks.append((self.current_time, running_pid))
            completed_proc, is_done = self.cpu.execute_tick(self.current_time)

            if is_done and completed_proc:
                self.completed_processes.append(completed_proc)
                self._log_event(
                    f"COMPLETION: {completed_proc.pid} finished execution. "
                    f"(CT={completed_proc.completion_time}, TAT={completed_proc.turnaround_time}, WT={completed_proc.waiting_time})"
                )

            self.current_time += 1

        self.timeline = self._compress_timeline(raw_ticks)
        self._log_event(f"Simulation completed at T={self.current_time}")
        return self.completed_processes


class PreemptivePriorityScheduler(BaseScheduler):
    """
    Preemptive Priority CPU Scheduler.
    
    At each clock cycle (tick), if a newly arrived process in the Ready Queue
    has a strictly higher priority (lower numeric priority value) than the
    currently executing process, the CPU is preempted. The current process is
    returned to the Ready Queue, and the higher-priority task is dispatched.
    """

    def run(self) -> List[PCB]:
        unadmitted: List[PCB] = list(self.processes)
        total_processes = len(unadmitted)
        self.current_time = 0
        raw_ticks: List[Tuple[int, Optional[str]]] = []

        self._log_event("Simulation started: Preemptive Priority Scheduling")

        while len(self.completed_processes) < total_processes:
            # 1. Admit all processes arriving at current_time into Ready Queue
            newly_arrived = [p for p in unadmitted if p.arrival_time == self.current_time]
            for p in newly_arrived:
                self.ready_queue.enqueue(p)
                unadmitted.remove(p)
                self._log_event(f"ARRIVAL: {p.pid} ('{p.task_type}', Prio={p.priority}, BT={p.burst_time}) entered Ready Queue")

            # 2. Check for Preemption if CPU is currently running a process
            if not self.cpu.is_idle() and not self.ready_queue.is_empty():
                top_candidate = self.ready_queue.peek()
                current_proc = self.cpu.current_process
                
                # Preemption condition: top candidate has strictly higher priority (lower number)
                if top_candidate.priority < current_proc.priority:
                    preempted_proc = self.cpu.preempt()
                    self._log_event(
                        f"PREEMPTION: {preempted_proc.pid} (Prio={preempted_proc.priority}, Rem={preempted_proc.remaining_burst_time}) "
                        f"preempted by {top_candidate.pid} (Prio={top_candidate.priority})"
                    )
                    self.ready_queue.enqueue(preempted_proc)

            # 3. If CPU is idle, dispatch the highest priority process from Ready Queue
            if self.cpu.is_idle():
                if not self.ready_queue.is_empty():
                    next_process = self.ready_queue.dequeue()
                    self.cpu.allocate(next_process, self.current_time)
                    self._log_event(f"DISPATCH: CPU allocated to {next_process.pid} (Prio={next_process.priority}, Rem={next_process.remaining_burst_time})")
                else:
                    # CPU remains idle during this tick
                    raw_ticks.append((self.current_time, None))
                    self._log_event("CPU IDLE: No ready processes in queue")
                    self.current_time += 1
                    continue

            # 4. Execute 1 tick on CPU
            running_pid = self.cpu.current_process.pid
            raw_ticks.append((self.current_time, running_pid))
            completed_proc, is_done = self.cpu.execute_tick(self.current_time)

            if is_done and completed_proc:
                self.completed_processes.append(completed_proc)
                self._log_event(
                    f"COMPLETION: {completed_proc.pid} finished execution. "
                    f"(CT={completed_proc.completion_time}, TAT={completed_proc.turnaround_time}, WT={completed_proc.waiting_time}, RT={completed_proc.response_time})"
                )

            self.current_time += 1

        self.timeline = self._compress_timeline(raw_ticks)
        self._log_event(f"Simulation completed at T={self.current_time}")
        return self.completed_processes
