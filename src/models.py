from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


class Status(Enum):
    PENDING = "В ожидании"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершено"


@dataclass
class Task:
    id: Optional[int]
    title: str
    description: str
    priority: Priority
    status: Status
    due_date: Optional[datetime]
    created_at: datetime
    category_id: Optional[int]


@dataclass
class Category:
    id: Optional[int]
    name: str
    color: str
    created_at: datetime