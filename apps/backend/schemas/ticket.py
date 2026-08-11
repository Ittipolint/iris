"""Ticket-related Pydantic models and enums."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, constr

TicketId = constr(pattern=r"^TKT-\d{3}$")


class TicketCategory(str, Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    ACCOUNT = "Account"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class CreateTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: TicketCategory
    priority: TicketPriority


class UpdateStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TicketStatus


class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: TicketId
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus = Field(default=TicketStatus.OPEN)


class SummaryResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
