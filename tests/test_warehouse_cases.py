"""
Unit Tests for Smart Warehouse OS Scheduling Simulation.

Covers:
- Test Case 1: Preemption verification (Urgent Order preempting Routine Restocking)
- Test Case 2: Non-Preemptive vs. Preemptive Comparative Benchmark
- Test Case 3: Full Warehouse Workload across all 7 task types
"""

import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pcb import PCB, ProcessState
from src.ready_queue import ReadyQueue
from src.cpu import SimulatedCPU
from src.scheduler import NonPreemptivePriorityScheduler, PreemptivePriorityScheduler
from src.metrics import PerformanceMetrics
from src.task_types import (
    TASK_URGENT_ORDER,
    TASK_NORMAL_ORDER,
    TASK_PICKING,
    TASK_PACKING,
    TASK_DISPATCH_PREPARATION,
    TASK_INVENTORY_UPDATE,
    TASK_RESTOCKING
)


class TestWarehouseScheduling(unittest.TestCase):

    def test_case_1_preemption_demonstration(self):
        """
        Verify that an incoming Urgent Order (Priority 1) immediately preempts
        an ongoing Routine Restocking task (Priority 3).
        """
        # P1: Restocking (Routine, Priority 3), AT=0, BT=8
        # P2: Urgent Order Processing (Urgent, Priority 1), AT=2, BT=3
        p1 = PCB("P1", TASK_RESTOCKING, arrival_time=0, burst_time=8, priority=3)
        p2 = PCB("P2", TASK_URGENT_ORDER, arrival_time=2, burst_time=3, priority=1)

        # 1. Non-Preemptive Execution
        np_scheduler = NonPreemptivePriorityScheduler([p1, p2])
        np_results = {p.pid: p for p in np_scheduler.run()}

        # In Non-Preemptive: P1 runs to completion (0 to 8), P2 waits and runs (8 to 11)
        self.assertEqual(np_results["P1"].completion_time, 8)
        self.assertEqual(np_results["P1"].turnaround_time, 8)
        self.assertEqual(np_results["P1"].waiting_time, 0)
        self.assertEqual(np_results["P1"].response_time, 0)

        self.assertEqual(np_results["P2"].completion_time, 11)
        self.assertEqual(np_results["P2"].turnaround_time, 9)  # 11 - 2
        self.assertEqual(np_results["P2"].waiting_time, 6)     # 9 - 3
        self.assertEqual(np_results["P2"].response_time, 6)    # 8 - 2

        self.assertEqual(np_scheduler.timeline, [(0, 8, "P1"), (8, 11, "P2")])

        # 2. Preemptive Execution
        p_scheduler = PreemptivePriorityScheduler([p1, p2])
        p_results = {p.pid: p for p in p_scheduler.run()}

        # In Preemptive: P1 runs (0 to 2), preempted by P2 (2 to 5), P1 resumes (5 to 11)
        self.assertEqual(p_results["P2"].start_time, 2)
        self.assertEqual(p_results["P2"].completion_time, 5)
        self.assertEqual(p_results["P2"].turnaround_time, 3)   # 5 - 2
        self.assertEqual(p_results["P2"].waiting_time, 0)      # 3 - 3
        self.assertEqual(p_results["P2"].response_time, 0)     # 2 - 2 (Immediate response!)

        self.assertEqual(p_results["P1"].completion_time, 11)
        self.assertEqual(p_results["P1"].turnaround_time, 11)  # 11 - 0
        self.assertEqual(p_results["P1"].waiting_time, 3)      # 11 - 8 (Waited while P2 executed)
        self.assertEqual(p_results["P1"].response_time, 0)     # 0 - 0

        self.assertEqual(p_scheduler.timeline, [(0, 2, "P1"), (2, 5, "P2"), (5, 11, "P1")])

    def test_case_2_comparative_benchmark(self):
        """
        Verify metric calculations and consistency under both algorithms
        for a 4-process staggered workload.
        """
        processes = [
            PCB("P1", TASK_PACKING, arrival_time=0, burst_time=6, priority=2),
            PCB("P2", TASK_INVENTORY_UPDATE, arrival_time=1, burst_time=4, priority=3),
            PCB("P3", TASK_URGENT_ORDER, arrival_time=2, burst_time=2, priority=1),
            PCB("P4", TASK_NORMAL_ORDER, arrival_time=3, burst_time=3, priority=2)
        ]

        # Test Non-Preemptive
        np_sched = NonPreemptivePriorityScheduler(processes)
        np_res = np_sched.run()
        np_metrics = PerformanceMetrics(np_res, np_sched.current_time)

        for p in np_res:
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)
            self.assertEqual(p.response_time, p.start_time - p.arrival_time)

        # Test Preemptive
        p_sched = PreemptivePriorityScheduler(processes)
        p_res = p_sched.run()
        p_metrics = PerformanceMetrics(p_res, p_sched.current_time)

        for p in p_res:
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)
            self.assertEqual(p.response_time, p.start_time - p.arrival_time)

        # In Preemptive, P3 (Urgent Order) must have lower Response Time and Waiting Time
        np_p3 = next(p for p in np_res if p.pid == "P3")
        p_p3 = next(p for p in p_res if p.pid == "P3")
        self.assertLessEqual(p_p3.response_time, np_p3.response_time)
        self.assertLessEqual(p_p3.waiting_time, np_p3.waiting_time)

    def test_case_3_full_warehouse_workload(self):
        """
        Verify full workload containing all 7 defined warehouse task types.
        """
        workload = [
            PCB("P1", TASK_RESTOCKING, arrival_time=0, burst_time=5, priority=3),
            PCB("P2", TASK_PICKING, arrival_time=1, burst_time=4, priority=2),
            PCB("P3", TASK_URGENT_ORDER, arrival_time=2, burst_time=3, priority=1),
            PCB("P4", TASK_PACKING, arrival_time=3, burst_time=2, priority=2),
            PCB("P5", TASK_DISPATCH_PREPARATION, arrival_time=4, burst_time=3, priority=2),
            PCB("P6", TASK_INVENTORY_UPDATE, arrival_time=6, burst_time=4, priority=3),
            PCB("P7", TASK_NORMAL_ORDER, arrival_time=7, burst_time=2, priority=2)
        ]

        total_burst = sum(p.burst_time for p in workload)

        # Preemptive run
        sched = PreemptivePriorityScheduler(workload)
        completed = sched.run()

        self.assertEqual(len(completed), 7)
        for p in completed:
            self.assertEqual(p.state, ProcessState.TERMINATED)
            self.assertTrue(p.is_completed())
            self.assertIsNotNone(p.completion_time)
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)
            self.assertEqual(p.response_time, p.start_time - p.arrival_time)

        # Since AT=0 and CPU is never idle while tasks are queued, total makespan = total_burst = 23
        self.assertEqual(sched.current_time, total_burst)


if __name__ == "__main__":
    unittest.main()
