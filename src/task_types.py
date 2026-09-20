"""
Task Types and Priority Mappings for Warehouse Operations.

In this simulation, warehouse tasks represent Operating System processes.
Priority Convention (strictly as per specification):
  Priority 1 = Highest priority / Urgent task
  Priority 2 = Normal task
  Priority 3 = Routine / Lower-priority task
"""

from typing import Dict

# Warehouse Task Type Definitions
TASK_URGENT_ORDER = "Urgent Order Processing"
TASK_NORMAL_ORDER = "Normal Order Processing"
TASK_PICKING = "Picking"
TASK_PACKING = "Packing"
TASK_DISPATCH_PREPARATION = "Dispatch Preparation"
TASK_INVENTORY_UPDATE = "Inventory Update"
TASK_RESTOCKING = "Restocking"

# Default Priority Mappings for Warehouse Tasks
DEFAULT_TASK_PRIORITIES: Dict[str, int] = {
    TASK_URGENT_ORDER: 1,         # Priority 1: Urgent
    TASK_NORMAL_ORDER: 2,         # Priority 2: Normal
    TASK_PICKING: 2,              # Priority 2: Normal
    TASK_PACKING: 2,              # Priority 2: Normal
    TASK_DISPATCH_PREPARATION: 2, # Priority 2: Normal
    TASK_INVENTORY_UPDATE: 3,     # Priority 3: Routine / Lower
    TASK_RESTOCKING: 3            # Priority 3: Routine / Lower
}

def get_default_priority(task_type: str) -> int:
    """Return default priority for a given task type, defaulting to 2 (Normal) if unknown."""
    return DEFAULT_TASK_PRIORITIES.get(task_type, 2)
