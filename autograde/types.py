import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Iterable,
    Protocol,
    Sequence,
    runtime_checkable,
)


@dataclass
class Submission:
    submission_key: str
    directory: Path
    submitted_at: datetime.datetime | None = None
    due_at: datetime.datetime | None = None
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SubmissionRecord:
    submission_key: str
    # [(relpath_under_submission, src_path), ...]
    files: Iterable[tuple[Path, Path]] | None = None
    handed_in: datetime.datetime | None = None
    due_date: datetime.datetime | None = None
    attrs: dict[str, Any] | None = None


@runtime_checkable
class Importer(Protocol):
    def __call__(self, file_path: Path) -> Iterable[SubmissionRecord] | None: ...


@runtime_checkable
class Normalizer(Protocol):
    def __call__(
        self, sdir: Path
    ) -> None: ...


@runtime_checkable
class AssignmentSpec(Protocol):
    key: ClassVar[str]
    title: ClassVar[str]
    required_files: ClassVar[Sequence[str]]
    importers: ClassVar[Sequence[Importer]]
    normalizers: ClassVar[Sequence[Normalizer]]
