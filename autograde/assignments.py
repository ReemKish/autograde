# autograde/assignments.py
from typing import ClassVar, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class AssignmentSpec(Protocol):
    key: ClassVar[str]
    title:ClassVar[str]
    required_submission_files: ClassVar[tuple[str, ...]]

def assignment(cls: type[AssignmentSpec]) -> type[AssignmentSpec]:
    register(cls)
    return cls

# @dataclass(frozen=True)
# class AssignmentSpec:
#     key: str
#     title: str
#     required_submission_files: List[str]
    # import_submissions: Importer
    # import_metadata: Optional[Importer] = None
    # normalizers: List[Normalizer] = field(default_factory=list)
    # tests_entrypoint: Optional[str] = None

_registry: Dict[str, type[AssignmentSpec]] = {}
_frozen = False

def register(*specs: type[AssignmentSpec], override: bool=False) -> None:
    if _frozen and not override:
        raise RuntimeError("Catalog frozen")
    for spec in specs:
        if spec.key in _registry and not override:
            raise ValueError(f"Duplicate assignment key: {spec.key!r}")
        _registry[spec.key] = spec

def get(key: str) -> type[AssignmentSpec]:
    try:
        return _registry[key]
    except KeyError:
        raise KeyError(f"Unknown assignment key: {key!r}") from None

def list_keys() -> List[str]:
    return sorted(_registry)

def freeze() -> None:
    global _frozen
    _frozen = True
