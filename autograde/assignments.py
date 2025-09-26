from typing import Dict, List

from autograde.types import AssignmentSpec


def assignment(cls: type[AssignmentSpec]) -> type[AssignmentSpec]:
    register(cls)
    return cls

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
