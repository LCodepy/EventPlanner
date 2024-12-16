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
    idx: int


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
                importance BLOB NOT NULL,
                idx INTEGER
            )
            """
        )
        self.conn.commit()

        self.tasks = self.load_tasks()

    def load_tasks(self) -> dict[int, Task]:
        with self.conn:
            self.cursor.execute(f"SELECT id, description, importance, idx FROM {self.database_name}")
            rows = self.cursor.fetchall()
            return {id_: Task(id_, description, pickle.loads(importance), idx) for id_, description, importance, idx in rows}

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        with self.conn:
            self.cursor.execute(
                f"INSERT INTO {self.database_name} VALUES (?, ?, ?, ?)", (task.id, task.description, pickle.dumps(task.importance), task.idx)
            )

    def remove_task(self, id_: int) -> None:
        self.tasks.pop(id_)
        with self.conn:
            self.cursor.execute(f"DELETE from {self.database_name} WHERE id = :id", {"id": id_})

    def update_task(self, id_: int, description: str = None, importance: TaskImportance = None, idx: int = None) -> None:
        conn = sqlite3.connect(Assets().todo_list_database_path)
        cursor = conn.cursor()

        new_task = Task(id_, description or self.tasks[id_].description, importance or self.tasks[id_].importance,
                        idx or self.tasks[id_].idx)
        with conn:
            cursor.execute(f"UPDATE {self.database_name} SET description = ?, importance = ?, idx = ? WHERE id = ?",
                            (new_task.description, pickle.dumps(new_task.importance), new_task.idx, id_))

    def get_next_id(self) -> int:
        ids = {i for i in range(len(self.tasks)+1)}
        return list(ids.difference(set(self.tasks.keys())))[0]

    def get_task(self, id_: int) -> Task:
        if id_ in self.tasks:
            return self.tasks[id_]

    def get_tasks(self) -> list[Task]:
        return list(self.tasks.values())

