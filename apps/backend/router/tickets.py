"""Ticket endpoints for the IT Ticket Tracker backend."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.backend.schemas.ticket import CreateTicketRequest, Ticket, TicketId, UpdateStatusRequest
from apps.backend.services.ticket_service import TicketService, get_ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _not_implemented(method_name: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"{method_name} is not implemented yet")


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(
    request: CreateTicketRequest,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    try:
        return service.create_ticket(request)
    except NotImplementedError:
        raise _not_implemented("create_ticket")


@router.get("", response_model=list[Ticket])
def list_tickets(
    status: str | None = None,
    service: TicketService = Depends(get_ticket_service),
) -> list[Ticket]:
    try:
        return service.list_tickets(status=status)
    except NotImplementedError:
        raise _not_implemented("list_tickets")


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket_by_id(
    ticket_id: TicketId,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    try:
        return service.get_ticket_by_id(ticket_id)
    except NotImplementedError:
        raise _not_implemented("get_ticket_by_id")


@router.patch("/{ticket_id}/status", response_model=Ticket)
def update_ticket_status(
    ticket_id: TicketId,
    request: UpdateStatusRequest,
    service: TicketService = Depends(get_ticket_service),
) -> Ticket:
    try:
        return service.update_ticket_status(ticket_id, request)
    except NotImplementedError:
        raise _not_implemented("update_ticket_status")
