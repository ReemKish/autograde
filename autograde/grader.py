from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self

@dataclass
class Assignment:
    id: str
    title: str
    description: str


@dataclass
class Submission:
    root: Path
    student_id: str
    submitted_at: datetime | None
    student_name: str | None

    def grade(self):
        # Placeholder for grading logic
        pass


@dataclass
class Grader:
    exercise: str
    title: str


@dataclass
class GradingEnvironment:
    root: Path
    assignment: Assignment
    submissions: list[Submission]

    @classmethod
    def from_path(cls, path: Path) -> Self | None:
        dotdir = path / ".autograde"
