"""Service layer for the IT Ticket Tracker backend."""

from .ticket_service import TicketService, get_ticket_service, ticket_service

__all__ = ["TicketService", "get_ticket_service", "ticket_service"]
