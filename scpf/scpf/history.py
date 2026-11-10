"""Experimental compiler-history controls for SCPF.

This module deliberately keeps policy separate from geometry. A behavior()
scope influences how semantic objects created inside that scope are lowered
to SolidCraft history.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum


class History(str, Enum):
    AUTO = "auto"
    NATIVE = "native"
    SKETCH = "sketch"


_history = ContextVar("scpf_history_policy", default=History.AUTO)


def active_history():
    return _history.get()


@contextmanager
def behavior(*, history=History.AUTO):
    try:
        history = History(history)
    except ValueError as exc:
        raise ValueError("history must be History.AUTO, NATIVE or SKETCH") from exc
    token = _history.set(history)
    try:
        yield
    finally:
        _history.reset(token)
