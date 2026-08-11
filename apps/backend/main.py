"""FastAPI application entrypoint for IT Ticket Tracker."""

from __future__ import annotations

from fastapi import FastAPI

from apps.backend.router import api_router
from apps.backend.services.ticket_service import ticket_service


def create_app(*, seed_data_enabled: bool = False) -> FastAPI:
    """Create a FastAPI app configured for the ticket tracker."""

    app = FastAPI(title="IT Ticket Tracker", version="0.1.0")
    ticket_service.initialize(seed_data_enabled=seed_data_enabled)
    app.include_router(api_router)
    return app


app = create_app()
