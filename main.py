"""
Smart Warehouse Automation Platform - OS CPU Scheduling Simulation
Review 1 Demonstration Entrypoint.

This script executes the simulation of warehouse tasks as operating system processes
using Priority Scheduling (Non-Preemptive and Preemptive), rendering Gantt charts,
event logs, and scheduling performance metrics.
"""

import sys
import argparse
from typing import List

from src.pcb import PCB
from src.scheduler import NonPreemptivePriorityScheduler, PreemptivePriorityScheduler
from src.metrics import PerformanceMetrics
from src.gantt import render_gantt_chart, render_process_table, render_comparison_table
from src.task_types import (
    TASK_URGENT_ORDER,
    TASK_NORMAL_ORDER,
    TASK_PICKING,
    TASK_PACKING,
    TASK_DISPATCH_PREPARATION,
    TASK_INVENTORY_UPDATE,
    TASK_RESTOCKING
)


def get_test_case_1() -> List[PCB]:
    """Test Case 1: Urgent Order Preemption Demonstration."""
    return [
        PCB("P1", TASK_RESTOCKING, arrival_time=0, burst_time=8, priority=3),
        PCB("P2", TASK_URGENT_ORDER, arrival_time=2, burst_time=3, priority=1),
    ]


def get_test_case_2() -> List[PCB]:
    """Test Case 2: Comparative Benchmark (4-task staggered workload)."""
    return [
        PCB("P1", TASK_PACKING, arrival_time=0, burst_time=6, priority=2),
        PCB("P2", TASK_INVENTORY_UPDATE, arrival_time=1, burst_time=4, priority=3),
        PCB("P3", TASK_URGENT_ORDER, arrival_time=2, burst_time=2, priority=1),
        PCB("P4", TASK_NORMAL_ORDER, arrival_time=3, burst_time=3, priority=2),
    ]


def get_test_case_3() -> List[PCB]:
    """Test Case 3: Complete Warehouse Workload (All 7 Warehouse Task Types)."""
    return [
        PCB("P1", TASK_RESTOCKING, arrival_time=0, burst_time=5, priority=3),
        PCB("P2", TASK_PICKING, arrival_time=1, burst_time=4, priority=2),
        PCB("P3", TASK_URGENT_ORDER, arrival_time=2, burst_time=3, priority=1),
        PCB("P4", TASK_PACKING, arrival_time=3, burst_time=2, priority=2),
        PCB("P5", TASK_DISPATCH_PREPARATION, arrival_time=4, burst_time=3, priority=2),
        PCB("P6", TASK_INVENTORY_UPDATE, arrival_time=6, burst_time=4, priority=3),
        PCB("P7", TASK_NORMAL_ORDER, arrival_time=7, burst_time=2, priority=2),
    ]


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)


def run_single_scheduler(scheduler_cls, workload: List[PCB], name: str):
    print_banner(f"Running: {name}")
    scheduler = scheduler_cls(workload)
    completed = scheduler.run()
    metrics = PerformanceMetrics(completed, scheduler.current_time)

    print("\n[EXECUTION LOG]")
    for ev in scheduler.events:
        print(f"  {ev}")

    print("\n[GANTT CHART]")
    print(render_gantt_chart(scheduler.timeline))

    print("\n[PROCESS PERFORMANCE TABLE]")
    print(render_process_table(completed))

    summary = metrics.get_summary()
    print("\n[SUMMARY METRICS]")
    print(f"  • Average Turnaround Time:     {summary['average_turnaround_time']} time units")
    print(f"  • Average Waiting Time:        {summary['average_waiting_time']} time units")
    print(f"  • Average Response Time:       {summary['average_response_time']} time units")

    return metrics


def run_comparative_demonstration(workload: List[PCB], title: str):
    print_banner(f"Comparative Study: {title}")
    
    print("\n[INPUT WORKLOAD - WAREHOUSE TASKS]")
    print(render_process_table(workload))

    metrics_np = run_single_scheduler(NonPreemptivePriorityScheduler, workload, "Non-Preemptive Priority Scheduling")
    metrics_p = run_single_scheduler(PreemptivePriorityScheduler, workload, "Preemptive Priority Scheduling")

    print_banner(f"Side-by-Side Comparison: {title}")
    print(render_comparison_table(metrics_np, metrics_p))


def main():
    parser = argparse.ArgumentParser(description="Smart Warehouse Automation Platform - OS Scheduling Simulation")
    parser.add_argument("--demo", action="store_true", help="Run all 3 test case demonstrations")
    parser.add_argument("--case1", action="store_true", help="Run Test Case 1: Urgent Order Preemption")
    parser.add_argument("--case2", action="store_true", help="Run Test Case 2: Comparative Benchmark")
    parser.add_argument("--case3", action="store_true", help="Run Test Case 3: Complete Warehouse Workload")

    args = parser.parse_args()

    print_banner("Smart Warehouse Automation Platform - OS PBL Review 1")
    print("Syllabus Scope: Unit 1 & Unit 2 up to Priority Scheduling")
    print("Priority Mapping: 1 = Urgent (Highest), 2 = Normal, 3 = Routine (Lower)")

    if args.case1:
        run_comparative_demonstration(get_test_case_1(), "Test Case 1 (Preemption Demonstration)")
    elif args.case2:
        run_comparative_demonstration(get_test_case_2(), "Test Case 2 (Comparative Benchmark)")
    elif args.case3:
        run_comparative_demonstration(get_test_case_3(), "Test Case 3 (Full 7-Task Workload)")
    else:
        # Default: run all 3 cases
        run_comparative_demonstration(get_test_case_1(), "Test Case 1 (Preemption Demonstration)")
        run_comparative_demonstration(get_test_case_2(), "Test Case 2 (Comparative Benchmark)")
        run_comparative_demonstration(get_test_case_3(), "Test Case 3 (Full 7-Task Workload)")


if __name__ == "__main__":
    main()
