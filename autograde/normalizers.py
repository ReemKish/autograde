from pathlib import Path
from typing import Sequence


class FilenameNormalizer:
    def __init__(self, required_files: Sequence[str | Path]) -> None:
        self.required_files = [Path(f) for f in required_files]

    def __call__(self, sdir: Path) -> None:
        required_filenames = {rf.name for rf in self.required_files}
        for path in sdir.rglob("*"):
            if path.is_file():
                if path.name not in required_filenames:
                    for method in (
                        str.title,
                        str.lower,
                        str.upper,
                        str.strip,
                        lambda s: s.strip("_"),  # 'main_.c' -> 'main.c'
                        lambda s: s.split()[0],  # 'file (1).txt' -> 'file.txt'
                    ):
                        new_name = method(path.stem) + path.suffix
                        if new_name in required_filenames:
                            target_path = path.parent / new_name
                            path.rename(target_path)
                            break


class StructureNormalizer:
    def __init__(
        self, required_files: Sequence[str | Path], *, prune: bool, flatten: bool
    ) -> None:
        self.required_files = [Path(f) for f in required_files]
        self.prune = prune
        self.flatten = flatten

    def __call__(self, sdir: Path) -> None:
        for path in sdir.rglob("*"):
            relpath = path.relative_to(sdir)
            if path.is_file():
                if any(relpath.match(str(rf)) for rf in self.required_files):
                    if self.flatten:
                        target_path = sdir / relpath.name
                        if path != target_path:
                            path.rename(target_path)
                    continue
                elif self.prune:
                    path.unlink()
        for path in sorted(sdir.rglob("*"), reverse=True):
            if self.prune and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
