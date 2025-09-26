import datetime as dt
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Self


@dataclass
class Assignment:
    id: str
    title: str
    description: str
    submission_files: list[str]

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)


@dataclass
class Submission:
    submission_key: str
    directory: Path
    handed_in: dt.datetime | None = None
    due_date: dt.datetime | None = None
    attrs: dict[str, Any] = field(default_factory=dict)
