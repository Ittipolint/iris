"""Application configuration for the IT Ticket Tracker backend."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    """Static settings used by the skeleton app."""

    seed_data_enabled: bool = False


settings = AppSettings()
