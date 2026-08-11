"""Business logic placeholders for the ticket tracker."""

from __future__ import annotations

from typing import Iterable

from apps.backend.schemas.ticket import CreateTicketRequest, SummaryResponse, Ticket, TicketId, UpdateStatusRequest
from apps.backend.state import reset_state, state


class TicketService:
    """In-memory service facade for ticket operations."""

    def initialize(self, *, seed_data_enabled: bool = False) -> None:
        reset_state(seed_data_enabled=seed_data_enabled)

    def reset(self, *, seed_data_enabled: bool = False) -> None:
        reset_state(seed_data_enabled=seed_data_enabled)

    def create_ticket(self, request: CreateTicketRequest) -> Ticket:
        raise NotImplementedError("create_ticket is not implemented yet")

    def list_tickets(self, *, status: str | None = None) -> list[Ticket]:
        raise NotImplementedError("list_tickets is not implemented yet")

    def get_ticket_by_id(self, ticket_id: TicketId) -> Ticket:
        raise NotImplementedError("get_ticket_by_id is not implemented yet")

    def update_ticket_status(self, ticket_id: TicketId, request: UpdateStatusRequest) -> Ticket:
        raise NotImplementedError("update_ticket_status is not implemented yet")

    def get_summary(self) -> SummaryResponse:
        raise NotImplementedError("get_summary is not implemented yet")

    def load_seed_data(self) -> list[Ticket]:
        raise NotImplementedError("load_seed_data is not implemented yet")

    def replace_tickets(self, tickets: Iterable[Ticket]) -> None:
        state.tickets = list(tickets)

    def snapshot_tickets(self) -> list[Ticket]:
        return list(state.tickets)


ticket_service = TicketService()


def get_ticket_service() -> TicketService:
    return ticket_service
