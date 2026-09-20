# Smart Warehouse Automation Platform (OS PBL)


**Course:** Operating Systems (CCSE0303A)  
**Milestone:** REVIEW 1  
**Target Syllabus Scope:** Unit 1 & Unit 2 up to **Priority Scheduling**

---

## 1. Project Overview & Scope Declaration

> **"This Review 1 implementation covers the Operating Systems concepts studied up to Pre-emptive and Non-Pre-emptive Priority Scheduling."**  
> **"The project will be extended in subsequent reviews as additional Operating Systems concepts are covered in the syllabus."**

This project is an **Operating Systems scheduling simulation** developed as part of Project-Based Learning (PBL). It models warehouse operations as simulated OS processes executing on a central processing resource.

### Important Conceptual Clarification
```
Warehouse Task = Simulated OS Process
```
The project is strictly an Operating Systems scheduling simulation. **It does NOT control:**
- Physical warehouse robots
- Physical workers
- IoT hardware
- Real warehouse machinery

This project does not claim to be the final complete warehouse automation platform. It is Review 1 of an incremental, multi-review academic project.

---

## 2. Review 1 Scope & Features

The Review 1 scope is strictly limited to:
1. **Warehouse tasks represented as processes**: Each task is modeled as an OS process.
2. **Process Attributes**:
   - **Task / Process ID** (`pid`): Unique identifier (e.g., `P1`, `P2`).
   - **Task Type**: Category of warehouse task (e.g., *Urgent Order Processing*, *Picking*).
   - **Arrival Time** ($AT$): Clock time when the task enters the system.
   - **Burst Time** ($BT$): Total CPU execution time required.
   - **Priority**: Task priority (1 = Highest, 2 = Normal, 3 = Routine).
   - **Process State**: Lifecycle stage (`NEW`, `READY`, `RUNNING`, `TERMINATED`).
3. **Simplified Process Control Block (PCB)**: In-memory structure holding process identity, scheduling parameters, remaining burst time, and performance accounting data.
4. **Ready Queue**: Priority-ordered queue holding processes waiting for CPU dispatch, with FCFS tie-breaking.
5. **Simulated CPU / Processing Resource**: Single-core CPU executing processes cycle-by-cycle.
6. **CPU / Short-Term Scheduler**: Selects the next ready process from the Ready Queue and dispatches it to the CPU.
7. **Priority Scheduling**:
   - **Non-Preemptive Priority Scheduling**: Once allocated, a process retains the CPU until its burst finishes.
   - **Preemptive Priority Scheduling**: When a new process arrives with strictly higher priority than the executing process, the running process is preempted back to the Ready Queue, and the higher-priority task is dispatched.
8. **Scheduling Performance Metrics**:
   - $\text{Completion Time } (CT)$: Time at which a process finishes execution.
   - $\text{Turnaround Time } (TAT) = CT - AT$
   - $\text{Waiting Time } (WT) = TAT - BT$
   - $\text{Response Time } (RT) = \text{First CPU Run Time} - AT$
   - $\text{Average Waiting Time } (\overline{WT})$
   - $\text{Average Turnaround Time } (\overline{TAT})$
   - $\text{Average Response Time } (\overline{RT})$
9. **Execution Order**: Chronological event logs showing arrivals, dispatches, preemptions, and completions.
10. **Gantt Chart**: Terminal-rendered ASCII Gantt charts showing process execution intervals.
11. **Warehouse-Specific Test Cases**: Reproducible test workloads demonstrating preemption, comparative scheduling behavior, and full-spectrum task handling.

---

## 3. Priority Mapping & Warehouse Task Types

Consistent with the project specification:
- **Priority 1 (Highest / Urgent)**: Critical warehouse operations that require immediate response.
- **Priority 2 (Normal)**: Standard daily fulfillment operations.
- **Priority 3 (Routine / Lower)**: Background, deferred, or maintenance activities.

| Warehouse Task Type | Default Priority | Priority Level | Description |
| :--- | :---: | :---: | :--- |
| **Urgent Order Processing** | **1** | Highest / Urgent | Express customer shipments requiring immediate fulfillment. |
| **Normal Order Processing** | **2** | Normal | Standard customer orders scheduled for regular fulfillment. |
| **Picking** | **2** | Normal | Item retrieval from warehouse storage bins. |
| **Packing** | **2** | Normal | Boxing and sealing picked goods. |
| **Dispatch Preparation** | **2** | Normal | Manifesting and staging goods at loading docks. |
| **Inventory Update** | **3** | Routine / Lower | Periodic reconciliation of stock count in database. |
| **Restocking** | **3** | Routine / Lower | Replenishing shelves from bulk receiving. |

---

## 4. Project Structure

```
smart_warehouse_os_pbl/
│
├── src/
│   ├── __init__.py           # Package marker
│   ├── pcb.py                # Process Control Block & ProcessState Enum
│   ├── task_types.py         # Warehouse task types and priority mappings
│   ├── ready_queue.py        # Priority Queue with FCFS tie-breaking
│   ├── cpu.py                # Simulated CPU processing resource
│   ├── scheduler.py          # Non-Preemptive and Preemptive Priority Schedulers
│   ├── metrics.py            # CT, TAT, WT, RT, and average metrics calculator
│   └── gantt.py              # Visual ASCII Gantt Chart & table renderers
│
├── tests/
│   ├── __init__.py           # Test package marker
│   └── test_warehouse_cases.py  # Automated unittests for all 3 test cases
│
├── main.py                   # Demonstration CLI and comparative benchmark runner
├── run_simulation.bat        # Windows launcher script
├── .gitignore                # Git ignore configuration
└── README.md                 # Complete documentation
```

---

## 5. How to Run the Project

### Prerequisites
- Python 3.8+ (Pure Python standard library; no external packages needed).

### Running Automated Tests
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running the Demonstration
```powershell
python main.py --demo
```

Individual test cases:
```powershell
python main.py --case1   # Urgent Order Preemption Demonstration
python main.py --case2   # 4-Process Comparative Benchmark
python main.py --case3   # Full 7-Task Warehouse Workload
```

### Windows One-Click Launcher
Double-click `run_simulation.bat` or execute in PowerShell:
```powershell
.\run_simulation.bat
```

---

## 6. Actual Test Cases & Generated Scheduling Results

The following results are generated directly from the simulation code and reflect actual execution outputs.

### Test Case 1: Urgent Order Preemption Demonstration
Demonstrates how an incoming Urgent Order (Priority 1) preempts an ongoing Routine Restocking process (Priority 3).

#### Workload Specification
| PID | Task Type | Priority | Arrival Time ($AT$) | Burst Time ($BT$) |
| :--- | :--- | :---: | :---: | :---: |
| **P1** | Restocking | 3 | 0 | 8 |
| **P2** | Urgent Order Processing | 1 | 2 | 3 |

#### Non-Preemptive Execution
- **Gantt Chart:**
  ```
  +--------------------+---------+
  |         P1         |    P2   |
  +--------------------+---------+
  0                    8        11
  ```
- **Process Performance Table:**
  ```
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | PID   | Task Type                 | Prio | AT  | BT  | CT  | TAT  | WT   | RT   |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | P1    | Restocking                | 3    | 0   | 8   | 8   | 8    | 0    | 0    |
  | P2    | Urgent Order Processing   | 1    | 2   | 3   | 11  | 9    | 6    | 6    |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  ```
- **Summary Metrics:**
  - Average Turnaround Time: 8.50
  - Average Waiting Time: 3.00
  - Average Response Time: 3.00

#### Preemptive Execution
- **Gantt Chart:**
  ```
  +--------+---------+------------------+
  |   P1   |    P2   |        P1        |
  +--------+---------+------------------+
  0        2         5                 11
  ```
- **Process Performance Table:**
  ```
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | PID   | Task Type                 | Prio | AT  | BT  | CT  | TAT  | WT   | RT   |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | P1    | Restocking                | 3    | 0   | 8   | 11  | 11   | 3    | 0    |
  | P2    | Urgent Order Processing   | 1    | 2   | 3   | 5   | 3    | 0    | 0    |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  ```
- **Summary Metrics:**
  - Average Turnaround Time: 7.00
  - Average Waiting Time: 1.50
  - Average Response Time: 0.00

#### Side-by-Side Comparison (Test Case 1)
| Metric | Non-Preemptive | Preemptive |
| :--- | :---: | :---: |
| **Average Turnaround Time (TAT)** | 8.50 | **7.00** |
| **Average Waiting Time (WT)** | 3.00 | **1.50** |
| **Average Response Time (RT)** | 3.00 | **0.00** |

---

### Test Case 2: Staggered 4-Process Comparative Benchmark
Evaluates a mixed workload of packing, inventory, urgent order, and normal order tasks.

#### Workload Specification
| PID | Task Type | Priority | Arrival Time ($AT$) | Burst Time ($BT$) |
| :--- | :--- | :---: | :---: | :---: |
| **P1** | Packing | 2 | 0 | 6 |
| **P2** | Inventory Update | 3 | 1 | 4 |
| **P3** | Urgent Order Processing | 1 | 2 | 2 |
| **P4** | Normal Order Processing | 2 | 3 | 3 |

#### Non-Preemptive Gantt Chart
```
+------------------+--------+---------+------------+
|        P1        |   P3   |    P4   |     P2     |
+------------------+--------+---------+------------+
0                  6        8         11          15
```

#### Preemptive Gantt Chart
```
+--------+--------+------------+---------+------------+
|   P1   |   P3   |     P1     |    P4   |     P2     |
+--------+--------+------------+---------+------------+
0        2        4            8         11          15
```

#### Side-by-Side Comparison (Test Case 2)
| Metric | Non-Preemptive | Preemptive |
| :--- | :---: | :---: |
| **Average Turnaround Time (TAT)** | 8.50 | **8.00** |
| **Average Waiting Time (WT)** | 4.75 | **4.25** |
| **Average Response Time (RT)** | 4.75 | **3.75** |

---

### Test Case 3: Complete 7-Task Warehouse Workload
Demonstrates full platform capability across all 7 warehouse task types.

#### Workload Specification
| PID | Task Type | Priority | Arrival Time ($AT$) | Burst Time ($BT$) |
| :--- | :--- | :---: | :---: | :---: |
| **P1** | Restocking | 3 | 0 | 5 |
| **P2** | Picking | 2 | 1 | 4 |
| **P3** | Urgent Order Processing | 1 | 2 | 3 |
| **P4** | Packing | 2 | 3 | 2 |
| **P5** | Dispatch Preparation | 2 | 4 | 3 |
| **P6** | Inventory Update | 3 | 6 | 4 |
| **P7** | Normal Order Processing | 2 | 7 | 2 |

#### Non-Preemptive Schedule
- **Gantt Chart:**
  ```
  +---------------+---------+------------+--------+---------+--------+------------+
  |       P1      |    P3   |     P2     |   P4   |    P5   |   P7   |     P6     |
  +---------------+---------+------------+--------+---------+--------+------------+
  0               5         8            12       14        17       19          23
  ```
- **Process Performance Table:**
  ```
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | PID   | Task Type                 | Prio | AT  | BT  | CT  | TAT  | WT   | RT   |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | P1    | Restocking                | 3    | 0   | 5   | 5   | 5    | 0    | 0    |
  | P2    | Picking                   | 2    | 1   | 4   | 12  | 11   | 7    | 7    |
  | P3    | Urgent Order Processing   | 1    | 2   | 3   | 8   | 6    | 3    | 3    |
  | P4    | Packing                   | 2    | 3   | 2   | 14  | 11   | 9    | 9    |
  | P5    | Dispatch Preparation      | 2    | 4   | 3   | 17  | 13   | 10   | 10   |
  | P6    | Inventory Update          | 3    | 6   | 4   | 23  | 17   | 13   | 13   |
  | P7    | Normal Order Processing   | 2    | 7   | 2   | 19  | 12   | 10   | 10   |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  ```
- **Summary Metrics:**
  - Average Turnaround Time: 10.71
  - Average Waiting Time: 7.43
  - Average Response Time: 7.43

#### Preemptive Schedule
- **Gantt Chart:**
  ```
  +--------+--------+---------+---------+--------+---------+--------+------------+------------+
  |   P1   |   P2   |    P3   |    P2   |   P4   |    P5   |   P7   |     P1     |     P6     |
  +--------+--------+---------+---------+--------+---------+--------+------------+------------+
  0        1        2         5         8        10        13       15           19          23
  ```
- **Process Performance Table:**
  ```
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | PID   | Task Type                 | Prio | AT  | BT  | CT  | TAT  | WT   | RT   |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  | P1    | Restocking                | 3    | 0   | 5   | 19  | 19   | 14   | 0    |
  | P2    | Picking                   | 2    | 1   | 4   | 8   | 7    | 3    | 0    |
  | P3    | Urgent Order Processing   | 1    | 2   | 3   | 5   | 3    | 0    | 0    |
  | P4    | Packing                   | 2    | 3   | 2   | 10  | 7    | 5    | 5    |
  | P5    | Dispatch Preparation      | 2    | 4   | 3   | 13  | 9    | 6    | 6    |
  | P6    | Inventory Update          | 3    | 6   | 4   | 23  | 17   | 13   | 13   |
  | P7    | Normal Order Processing   | 2    | 7   | 2   | 15  | 8    | 6    | 6    |
  +-------+---------------------------+------+-----+-----+-----+------+------+------+
  ```
- **Summary Metrics:**
  - Average Turnaround Time: **10.00**
  - Average Waiting Time: **6.71**
  - Average Response Time: **4.29**

#### Side-by-Side Comparison (Test Case 3)
| Metric | Non-Preemptive | Preemptive |
| :--- | :---: | :---: |
| **Average Turnaround Time (TAT)** | 10.71 | **10.00** |
| **Average Waiting Time (WT)** | 7.43 | **6.71** |
| **Average Response Time (RT)** | 7.43 | **4.29** |

---

## 7. Review 1 Scope Limits & Progressive Roadmap

To maintain strict fidelity to the syllabus and course progression:

### What is Explicitly Excluded from Review 1:
- Round Robin (RR)
- Multilevel Queue (MLQ)
- Multilevel Feedback Queue (MLFQ)
- Process Synchronization & Classical Problems (Bounded Buffer, Dining Philosophers)
- Deadlocks & Bankers Algorithm
- Memory Management (Paging, Segmentation, Page Replacement)
- Virtual Memory & File Systems
- External robotics / IoT hardware integration

### Progressive Roadmap:
- **Review 1 (Current):** Foundational OS processes, PCB structure, Ready Queue, CPU simulation, Priority Scheduling (Non-Preemptive & Preemptive), performance metrics (CT, TAT, WT, RT, and averages), Gantt chart visualization.
- **Review 2 (Next Milestone):** Extend the same codebase with topics covered in Module 2 & 3 (Round Robin, Multilevel Queue, Process Synchronization, Semaphores, Deadlock detection/avoidance).
- **Final Review:** Full end-to-end integration across all covered OS units into a unified Smart Warehouse Platform.
