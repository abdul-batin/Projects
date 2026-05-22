"""
Functional requirements:
1. Users can add,update,delete and view tasks.
2. Each task should have a title, description, due date and status
3. Users can mark tasks as completed or pending.
4. Users can view tasks based on their status (completed or pending).
5. Users can set reminders for tasks.
6. Users can categorize tasks into different projects or labels.
7. Users can prioritize tasks (e.g., high, medium, low).
8. Users can search for tasks by title or description.
9. Users can be notified of upcoming due dates for tasks.

Non-functional requirements:
1. The system should be user-friendly and intuitive.
2. Multiple users should be able to use the system simultaneously without conflicts.
3. The system should be responsive and perform well even with a large number of tasks.

"""

from enum import Enum

class Status(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class User:
    
     