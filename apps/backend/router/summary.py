"""Summary endpoint for the IT Ticket Tracker backend."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from apps.backend.schemas.ticket import SummaryResponse
from apps.backend.services.ticket_service import TicketService, get_ticket_service

router = APIRouter(tags=["summary"])


def _not_implemented(method_name: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"{method_name} is not implemented yet")


@router.get("/summary", response_model=SummaryResponse)
def get_summary(service: TicketService = Depends(get_ticket_service)) -> SummaryResponse:
    try:
        return service.get_summary()
    except NotImplementedError:
        raise _not_implemented("get_summary")
