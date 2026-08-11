"""API routers for the IT Ticket Tracker backend."""

from fastapi import APIRouter

from .summary import router as summary_router
from .tickets import router as tickets_router

api_router = APIRouter()
api_router.include_router(tickets_router)
api_router.include_router(summary_router)

__all__ = ["api_router"]
