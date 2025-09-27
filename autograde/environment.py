import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Mapping, Self

import autograde
from autograde.assignments import AssignmentSpec
from autograde.types import Submission, SubmissionRecord


@dataclass
class GradingEnvironment:
    root: Path
    assignment: type[AssignmentSpec]
    submissions: dict[str, Submission]

    submissions_dirname: ClassVar[str] = "submissions"
    metadata_filename: ClassVar[str] = "autograde.json"

    # def __init__(
    #     self,
    #     root: str | Path,
    #     assignment: type[AssignmentSpec],
    #     submissions: Mapping[str, Submission],
    # ):
    #     self.root = Path(root)
    #     self.assignment = assignment
    #     self.submissions = dict(submissions)

    # def __init__(self, root: str | Path, assignment_key: str | None = None):
    #     root = Path(root)
    #     if root.exists():
    #         try:
    #             self._load(root)
    #         except FileNotFoundError:
    #             raise FileExistsError(
    #                 f"Directory {root} already exists and is not a valid grading environment"
    #             ) from None
    #     else:
    #         assert (
    #             assignment_key is not None
    #         ), "Must provide assignment_key when initializing new environment"
    #         self.root = root
    #         self.assignment = autograde.assignments.get(assignment_key)
    #         self.submissions = {}

    def save(self) -> None:
        (self.root / self.submissions_dirname).mkdir(parents=True, exist_ok=True)
        with (self.root / self.metadata_filename).open("w") as f:
            json.dump(
                {
                    "assignment_key": self.assignment.key,
                    "submissions": {
                        sub.submission_key: {
                            "submitted_at": sub.submitted_at
                            and sub.submitted_at.isoformat(),
                            "due_at": sub.due_at and sub.due_at.isoformat(),
                            "attrs": sub.attrs,
                        }
                        for sub in self.submissions.values()
                    },
                },
                f,
                indent=2,
            )

    @classmethod
    def load(cls, path: str | Path):
        path = Path(path)
        metadata_file = path / cls.metadata_filename
        submissions_dir = path / cls.submissions_dirname
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

        return cls(
            root=path,
            assignment=assignment,
            submissions=submissions,
        )

    @classmethod
    def new(cls, path: str | Path, assignment_key: str) -> Self:
        path = Path(path)
        if path.exists():
            raise FileExistsError(f"Directory {path} already exists")
        self = cls(
            root=path,
            assignment=autograde.assignments.get(assignment_key),
            submissions={},
        )
        self.save()
        return self

    def import_from(self, source: str | Path) -> None:
        source = Path(source)
        for importer in self.assignment.importers:
            if (records := importer(source)) is not None:
                for record in records:
                    self.update(record)
                break
        else:
            logging.warning(f"No importer could handle source file: {source}")

    def update(self, record: SubmissionRecord) -> None:
        if record.submission_key not in self.submissions:
            self.submissions[record.submission_key] = Submission(
                submission_key=record.submission_key,
                directory=self.root / self.submissions_dirname / record.submission_key,
            )
        submission = self.submissions[record.submission_key]
        submission.submitted_at = record.handed_in or submission.submitted_at
        submission.due_at = record.due_date or submission.due_at
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

        # Run normalizers.
        for normalize in self.assignment.normalizers:
            normalize(sdir)

        self.save()
