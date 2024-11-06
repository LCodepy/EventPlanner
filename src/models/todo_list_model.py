import pickle
import sqlite3
from dataclasses import dataclass
from enum import Enum, auto

from src.utils.assets import Assets


class TaskImportance(Enum):

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


@dataclass
class Task:

    id: int
    description: str
    importance: TaskImportance


class TodoListModel:

    def __init__(self) -> None:
        self.database_name = "todo_list"
        self.conn = sqlite3.connect(Assets().todo_list_database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.database_name} (
                id INTEGER PRIMARY KEY,
                description TEXT,
                importance BLOB NOT NULL
            )
            """
        )
        self.conn.commit()

        self.tasks = self.load_tasks()

    def load_tasks(self) -> dict[int, Task]:
        with self.conn:
            self.cursor.execute(f"SELECT id, description, importance FROM {self.database_name}")
            rows = self.cursor.fetchall()
            return {id_: Task(id_, description, pickle.loads(importance)) for id_, description, importance in rows}

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        with self.conn:
            self.cursor.execute(
                f"INSERT INTO {self.database_name} VALUES (?, ?, ?)", (task.id, task.description, pickle.dumps(task.importance))
            )

    def remove_task(self, id_: int) -> None:
        self.tasks.pop(id_)
        with self.conn:
            self.cursor.execute(f"DELETE from {self.database_name} WHERE id = :id", {"id": id_})

    def get_next_id(self) -> int:
        ids = {i for i in range(len(self.tasks)+1)}
        return list(ids.difference(set(self.tasks.keys())))[0]

    def get_task(self, id_: int) -> Task:
        if id_ in self.tasks:
            return self.tasks[id_]

    def get_tasks(self) -> list[Task]:
        return list(self.tasks.values())

