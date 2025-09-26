import datetime
import json
import logging
import shutil
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any, ClassVar, Iterable, Protocol

import autograde
from autograde.assignments import AssignmentSpec
from autograde.models import Submission


@dataclass(frozen=True)
class SubmissionRecord:
    submission_key: str
    # [(relpath_under_submission, src_path), ...]
    files: Iterable[tuple[Path, Path]] | None = None
    handed_in: datetime.datetime | None = None
    due_date: datetime.datetime | None = None
    attrs: dict[str, Any] | None = None


class IngestSource(Protocol):
    def records(self) -> Iterable[SubmissionRecord]: ...


@dataclass
class GradingEnvironment:
    root: Path
    assignment: type[AssignmentSpec]
    submissions: dict[str, Submission]

    submissions_dirname: ClassVar[str] = "submissions"
    metadata_filename: ClassVar[str] = "autograde.json"

    def __init__(self, root: str | Path, assignment_key: str | None = None):
        root = Path(root)
        if root.exists():
            try:
                self._load(root)
            except FileNotFoundError:
                raise FileExistsError(
                    f"Directory {root} already exists and is not a valid grading environment"
                ) from None
        else:
            assert (
                assignment_key is not None
            ), "Must provide assignment_key when initializing new environment"
            self.root = root
            self.assignment = autograde.assignments.get(assignment_key)
            self.submissions = {}

    def save(self) -> None:
        (self.root / self.submissions_dirname).mkdir(parents=True, exist_ok=True)
        with (self.root / self.metadata_filename).open("w") as f:
            json.dump(
                {
                    "assignment_key": self.assignment.key,
                    "submissions": {
                        sub.submission_key: {
                            "handed_in": sub.handed_in.isoformat()
                            if sub.handed_in
                            else None,
                            "due_date": sub.due_date.isoformat()
                            if sub.due_date
                            else None,
                            "attrs": sub.attrs,
                        }
                        for sub in self.submissions.values()
                    },
                },
                f,
                indent=2,
            )

    def _load(self, path: str | Path):
        assert (
            not hasattr(self, "root") or getattr(self, "root") is None
        ), "Environment already loaded"
        path = Path(path)
        metadata_file = path / self.metadata_filename
        submissions_dir = path / self.submissions_dirname
        if not (path.exists() and metadata_file.exists() and submissions_dir.exists()):
            raise FileNotFoundError(f"Not a valid grading environment: {path}")
        with metadata_file.open("r") as f:
            data = json.load(f)
        assignment_key = data["assignment_key"]
        try:
            assignment = autograde.assignments.get(assignment_key)
        except KeyError:
            raise KeyError(
                f"Unknown assignment key {assignment_key!r} in grading environment at {path}"
            ) from None
        submissions = {
            submission_key: Submission(
                submission_key=submission_key,
                directory=submissions_dir / submission_key,
                attrs=attrs,
            )
            for submission_key, attrs in data.get("submissions", {}).items()
        }

        self.root = path
        self.assignment = assignment
        self.submissions = submissions

    def ingest(self, *sources: IngestSource) -> None:
        for record in chain(*(source.records() for source in sources)):
            self.update(record)

    def update(self, record: SubmissionRecord) -> None:
        if record.submission_key not in self.submissions:
            self.submissions[record.submission_key] = Submission(
                submission_key=record.submission_key,
                directory=self.root / self.submissions_dirname / record.submission_key,
            )
        submission = self.submissions[record.submission_key]
        submission.handed_in = record.handed_in or submission.handed_in
        submission.due_date = record.due_date or submission.due_date
        submission.attrs.update(record.attrs or {})
        sdir = submission.directory
        sdir.mkdir(parents=True, exist_ok=True)

        # Perform file updates.
        for relpath, src_path in record.files or []:
            dest_path = sdir / relpath
            if src_path.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            else:
                if dest_path.exists():
                    logging.debug(f"Overwriting existing file: {dest_path}")
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src_path, dest_path)

        # Run normalizers
        # for normalizer in sorted(
        #     autograde.normalizers.all(), key=lambda n: n.order
        # ):
        #     logging.debug(
        #         f"Running normalizer {normalizer.name} for submission {record.student_key}"
        #     )
        #     normalizer(self, record.student_key, sdir)


class Normalizer(Protocol):
    name: str
    order: int

    def __call__(
        self, env: GradingEnvironment, student_key: str, sdir: Path
    ) -> None: ...
