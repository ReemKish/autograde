from abc import ABC, abstractmethod
import zipfile
import os
from pathlib import Path

from autograde.grader import GradingEnvironment


class Importer(ABC):
    @abstractmethod
    def handle(self, filepath: Path, genv: GradingEnvironment) -> None:
        assert filepath.exists(), "File does not exist"

    @abstractmethod
    def should_handle(self, filepath: Path) -> bool:
        pass

class MoodleZipImporter(Importer):
    def should_handle(self, filepath: Path) -> bool:
        return filepath.suffix == ".zip"

    def handle(self, filepath: Path, genv: GradingEnvironment) -> None:
        """Extract all submissions from submissions_archive_filepath into dest_dir."""
        super().handle(filepath, genv)
        print(f"Importing submissions from {filepath}")
        submissions_archive_basename = filepath.name
        # logger.info(f"Unzipping submissions archive: {submissions_archive_basename}")
        try:
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(genv.root)
        except zipfile.BadZipFile as e:
            print(f"{filepath}: {e}")
            # logger.error(f"{submissions_archive_filepath}: {e}")
