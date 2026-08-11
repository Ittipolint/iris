from __future__ import annotations

import pytest
from pydantic import ValidationError

from apps.backend.schemas.ticket import (
    CreateTicketRequest,
    SummaryResponse,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    UpdateStatusRequest,
)
from apps.backend.services.ticket_service import TicketService, ticket_service
from apps.backend.state import reset_state, state


def _seed_three_tickets() -> None:
    ticket_service.replace_tickets(
        [
            Ticket(id="TKT-001", category=TicketCategory.HARDWARE, priority=TicketPriority.HIGH, status=TicketStatus.OPEN),
            Ticket(
                id="TKT-002",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.IN_PROGRESS,
            ),
            Ticket(
                id="TKT-003",
                category=TicketCategory.NETWORK,
                priority=TicketPriority.LOW,
                status=TicketStatus.RESOLVED,
            ),
        ]
    )
    state.ticket_id_counter = 3


def test_UT_001_create_ticket_assigns_system_generated_id_and_default_status() -> None:
    service = TicketService()
    request = CreateTicketRequest(category=TicketCategory.HARDWARE, priority=TicketPriority.HIGH)

    ticket = service.create_ticket(request)

    assert ticket.id.startswith("TKT-")
    assert ticket.status == TicketStatus.OPEN


def test_UT_002_create_ticket_rejects_missing_required_field() -> None:
    with pytest.raises(ValidationError):
        CreateTicketRequest(category=TicketCategory.SOFTWARE)


def test_UT_003_create_ticket_rejects_invalid_category() -> None:
    with pytest.raises(ValidationError):
        CreateTicketRequest(category="Printer", priority=TicketPriority.LOW)


def test_UT_004_create_ticket_rejects_invalid_priority() -> None:
    with pytest.raises(ValidationError):
        CreateTicketRequest(category=TicketCategory.NETWORK, priority="Urgent")


def test_UT_005_list_tickets_returns_all_items_from_in_memory_store() -> None:
    service = TicketService()
    _seed_three_tickets()
    tickets = service.list_tickets()
    assert len(tickets) == 3


def test_UT_006_filter_tickets_by_status_returns_only_matching_items() -> None:
    service = TicketService()
    _seed_three_tickets()
    tickets = service.list_tickets(status=TicketStatus.OPEN.value)
    assert all(ticket.status == TicketStatus.OPEN for ticket in tickets)


def test_UT_007_filter_tickets_by_status_returns_empty_list_when_no_match() -> None:
    service = TicketService()
    ticket_service.replace_tickets(
        [
            Ticket(id="TKT-001", category=TicketCategory.HARDWARE, priority=TicketPriority.HIGH, status=TicketStatus.RESOLVED),
        ]
    )
    tickets = service.list_tickets(status=TicketStatus.OPEN.value)
    assert tickets == []


def test_UT_008_get_ticket_by_id_returns_matching_ticket() -> None:
    service = TicketService()
    _seed_three_tickets()
    ticket = service.get_ticket_by_id("TKT-001")
    assert ticket.id == "TKT-001"


def test_UT_009_get_ticket_by_id_raises_when_ticket_not_found() -> None:
    service = TicketService()
    _seed_three_tickets()
    with pytest.raises(NotImplementedError):
        service.get_ticket_by_id("TKT-999")


def test_UT_010_ticket_id_must_match_required_format() -> None:
    with pytest.raises(ValidationError):
        Ticket(id="TK-001", category=TicketCategory.HARDWARE, priority=TicketPriority.HIGH, status=TicketStatus.OPEN)


def test_UT_011_update_ticket_status_changes_status_to_allowed_value() -> None:
    service = TicketService()
    _seed_three_tickets()
    request = UpdateStatusRequest(status=TicketStatus.RESOLVED)
    ticket = service.update_ticket_status("TKT-001", request)
    assert ticket.status == TicketStatus.RESOLVED


def test_UT_012_update_ticket_status_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        UpdateStatusRequest(status="Closed")


def test_UT_013_update_ticket_status_with_same_value_keeps_summary_consistent() -> None:
    service = TicketService()
    _seed_three_tickets()
    request = UpdateStatusRequest(status=TicketStatus.OPEN)
    ticket = service.update_ticket_status("TKT-001", request)
    assert ticket.status == TicketStatus.OPEN


def test_UT_014_summary_counts_match_current_tickets() -> None:
    service = TicketService()
    _seed_three_tickets()
    summary = service.get_summary()
    assert summary.total == 3
    assert summary.open == 1
    assert summary.in_progress == 1
    assert summary.resolved == 1


def test_UT_015_summary_counts_reflect_latest_state_without_cache() -> None:
    service = TicketService()
    _seed_three_tickets()
    summary_before = service.get_summary()
    ticket_service.replace_tickets(
        [
            *ticket_service.snapshot_tickets(),
            Ticket(
                id="TKT-004",
                category=TicketCategory.ACCOUNT,
                priority=TicketPriority.LOW,
                status=TicketStatus.OPEN,
            ),
        ]
    )
    state.ticket_id_counter = 4
    summary_after = service.get_summary()
    assert summary_before.total == 3
    assert summary_after.total == 4


def test_UT_016_seed_enabled_initializes_three_tickets_across_three_statuses() -> None:
    service = TicketService()
    service.initialize(seed_data_enabled=True)
    assert len(state.tickets) == 3
    assert {ticket.status for ticket in state.tickets} == {
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED,
    }


def test_UT_017_seed_disabled_starts_with_empty_state() -> None:
    reset_state(seed_data_enabled=False)
    assert state.tickets == []
    assert state.ticket_id_counter == 0
