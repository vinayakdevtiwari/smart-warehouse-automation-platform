"""
ASCII Gantt Chart and Process Performance Table Formatter.

Generates:
1. Visual ASCII Gantt Charts illustrating scheduling intervals and timeline.
2. Formatted process performance tables (PID, Task Type, Priority, AT, BT, CT, TAT, WT, RT).
3. Comparative performance tables comparing Non-Preemptive vs. Preemptive Priority Scheduling.
"""

from typing import List, Tuple, Optional
from src.pcb import PCB
from src.metrics import PerformanceMetrics


def render_gantt_chart(timeline: List[Tuple[int, int, Optional[str]]]) -> str:
    """
    Render an ASCII Gantt Chart from compressed timeline intervals.
    
    Format:
    +--------+--------+--------+
    |   P1   |   P2   |  IDLE  |
    +--------+--------+--------+
    0        4        8        12
    """
    if not timeline:
        return "[Empty Timeline]"

    top_border = "+"
    content_line = "|"
    bottom_border = "+"
    time_line = ""

    for idx, (start, end, pid) in enumerate(timeline):
        duration = end - start
        label = pid if pid is not None else "IDLE"
        
        # Block width proportional to duration, minimum 8 characters
        block_width = max(8, min(20, duration * 3))
        centered_label = label.center(block_width)

        top_border += "-" * block_width + "+"
        content_line += centered_label + "|"
        bottom_border += "-" * block_width + "+"

        # Time marker formatting
        str_start = str(start)
        if idx == 0:
            time_line += str_start.ljust(block_width + 1)
        else:
            time_line += str_start.ljust(block_width + 1)

    # Append the final end time
    final_time = str(timeline[-1][1])
    time_line = time_line.rstrip() + " " * max(1, (len(bottom_border) - len(time_line.rstrip()) - len(final_time))) + final_time

    return "\n".join([top_border, content_line, bottom_border, time_line])


def render_process_table(processes: List[PCB]) -> str:
    """
    Render a clean ASCII table of process metrics.
    """
    headers = ["PID", "Task Type", "Prio", "AT", "BT", "CT", "TAT", "WT", "RT"]
    row_format = "| {:<5} | {:<25} | {:<4} | {:<3} | {:<3} | {:<3} | {:<4} | {:<4} | {:<4} |"
    separator = "+-------+---------------------------+------+-----+-----+-----+------+------+------+"

    lines = [
        separator,
        row_format.format(*headers),
        separator
    ]

    for p in sorted(processes, key=lambda x: x.pid):
        lines.append(row_format.format(
            p.pid,
            p.task_type[:25],
            p.priority,
            p.arrival_time,
            p.burst_time,
            p.completion_time if p.completion_time is not None else "-",
            p.turnaround_time if p.turnaround_time is not None else "-",
            p.waiting_time if p.waiting_time is not None else "-",
            p.response_time if p.response_time is not None else "-"
        ))

    lines.append(separator)
    return "\n".join(lines)


def render_comparison_table(metrics_np: PerformanceMetrics, metrics_p: PerformanceMetrics) -> str:
    """
    Render a side-by-side comparison table between Non-Preemptive and Preemptive Priority Scheduling.
    Strictly aligned with Review 1 PBL scope (CT, TAT, WT, RT, and averages).
    """
    sep = "+-------------------------------------+-----------------+-----------------+"
    header = "| Metric                              | Non-Preemptive  | Preemptive      |"
    row = "| {:<35} | {:<15} | {:<15} |"

    lines = [
        sep,
        header,
        sep,
        row.format("Average Turnaround Time (TAT)", f"{metrics_np.avg_tat:.2f}", f"{metrics_p.avg_tat:.2f}"),
        row.format("Average Waiting Time (WT)", f"{metrics_np.avg_wt:.2f}", f"{metrics_p.avg_wt:.2f}"),
        row.format("Average Response Time (RT)", f"{metrics_np.avg_rt:.2f}", f"{metrics_p.avg_rt:.2f}"),
        sep
    ]

    return "\n".join(lines)
