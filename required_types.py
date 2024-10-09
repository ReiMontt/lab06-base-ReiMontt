"""Common types across Chopsticks components

Do not modify this file or copy-paste it into your code; simply import
a symbol (e.g., `Action`) via `from required_types import Action` in your
code while ensuring that `required_types.py` is in the same directory as
your code.

You are expected to go through and understand everything in this file.
"""

from __future__ import annotations
from typing import NewType, Protocol
from enum import StrEnum


PlayerId = NewType('PlayerId', int)
HandId = NewType('HandId', int)


class Action(StrEnum):
    TAP = 'Tap'
    SPLIT = 'Split'


class HandInfo(Protocol):
    @property
    def hand_id(self) -> HandId:
        """Return a `HandId` that is unique among all hands of the owning player."""
        ...

    @property
    def player_id(self) -> PlayerId:
        """Return the `PlayerId` of the owning player."""
        ...

    @property
    def fingers_up(self) -> int:
        """Return the number of fingers of the hand that are currently up."""
        ...

    @property
    def total_fingers(self) -> int:
        """Return the number of total fingers of the hand.

        While this should return 5 for normal human hands, the game should
        be able to accommodate hands with any positive number of fingers.
        """
        ...

    def is_active(self) -> bool:
        """Return whether the hand is active."""
        ...

    def is_inactive(self) -> bool:
        """Return whether the hand is inactive."""
        ...

    def to(self, fingers_up: int) -> HandInfo | None:
        """Return a copy of the `HandInfo` object with a new value for `fingers_up`.

        As `HandInfo` is expected to be immutable, this method can be used to
        "update" the `fingers_up` field of the existing `HandInfo` object by
        creating a _new_ object with its field values copied from the original
        except for `fingers_up` which is taken from the `fingers_up` parameter. 
        """
        ...
