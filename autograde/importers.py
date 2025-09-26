import csv
import datetime as dt
import logging
import re
import tempfile
import zipfile
from pathlib import Path
from typing import ClassVar, Iterable

from autograde.environment import SubmissionRecord


class MoodleAssignmentsArchiveImporter:
    def __call__(self, file_path: Path) -> Iterable[SubmissionRecord] | None:
        if not file_path.is_file() or file_path.suffix.lower() != ".zip":
            return None
        logging.info(f"Extracting submissions from Moodle zip archive: {file_path}")
        with tempfile.TemporaryDirectory() as submission_tmp_dir_name:
            submission_tmp_dir = Path(submission_tmp_dir_name)
            with zipfile.ZipFile(file_path, "r") as zf:
                zf.extractall(submission_tmp_dir)

            for dir in submission_tmp_dir.iterdir():
                m = re.match(
                    r"^(?P<name>.+)_(?P<id>\d+)_assignsubmission_file$", dir.name
                )
                if not m:
                    logging.warning(f"Skipping unrecognized directory: {dir}")
                    continue
                student_name = m.group("name")
                student_canonical_name = (
                    student_name.replace(" ", "_").replace(" ", "_").lower()
                )
                student_id = m.group("id")
                yield SubmissionRecord(
                    submission_key=f"{student_canonical_name}-{student_id}",
                    files=[
                        (filepath.relative_to(dir), filepath)
                        for filepath in dir.rglob("*")
                    ],
                    attrs={"student_name": student_name, "student_id": student_id},
                )


class MoodleGradingWorksheetImporter:
    MOODLE_CSV_TIME_FORMAT: ClassVar[str] = "%A, %d %B %Y, %H:%M"

    def _parse_csv_time(self, time_str: str) -> dt.datetime | None:
        try:
            return dt.datetime.strptime(time_str, self.MOODLE_CSV_TIME_FORMAT)
        except ValueError:
            raise ValueError(f"Invalid time format in Moodle CSV: {time_str!r}") from None

    def __call__(self, file_path: Path) -> Iterable[SubmissionRecord] | None:
        if not file_path.is_file() or file_path.suffix.lower() != ".csv":
            return None
        logging.info(f"Reading metadata from Moodle grading worksheet: {file_path}")
        with file_path.open(newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student_id = row["\ufeffIdentifier"][len("Participant ") :]
                student_name = row["Full name"]
                status = row["Status"]
                handed_in = self._parse_csv_time(row["Last modified (submission)"])
                due_date = self._parse_csv_time(row["Due date"])
                if status.startswith("No submission") or not handed_in:
                    continue
                student_canonical_name = (
                    student_name.replace(" ", "_").replace(" ", "_").lower()
                )
                yield SubmissionRecord(
                    submission_key=f"{student_canonical_name}-{student_id}",
                    attrs={
                        "student_name": student_name,
                        "student_id": student_id,
                    },
                    handed_in=handed_in,
                    due_date=due_date,
                )
