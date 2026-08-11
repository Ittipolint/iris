"""Shared in-memory state for the backend skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InMemoryState:
    tickets: list[Any] = field(default_factory=list)
    ticket_id_counter: int = 0
    seed_data_enabled: bool = False

    def reset(self, *, seed_data_enabled: bool = False) -> None:
        self.tickets.clear()
        self.ticket_id_counter = 0
        self.seed_data_enabled = seed_data_enabled


state = InMemoryState()


def reset_state(*, seed_data_enabled: bool = False) -> None:
    state.reset(seed_data_enabled=seed_data_enabled)
