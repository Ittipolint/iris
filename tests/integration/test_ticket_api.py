from __future__ import annotations

from fastapi.testclient import TestClient

from apps.backend.main import create_app
from apps.backend.schemas.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from apps.backend.services.ticket_service import ticket_service
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


def test_IT_001_create_ticket_via_post_tickets_success(client: TestClient) -> None:
    response = client.post("/tickets", json={"category": "Hardware", "priority": "Medium"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("TKT-")
    assert body["status"] == "Open"


def test_IT_002_post_tickets_rejects_missing_required_field(client: TestClient) -> None:
    response = client.post("/tickets", json={"category": "Software"})
    assert response.status_code == 422


def test_IT_003_post_tickets_rejects_invalid_category(client: TestClient) -> None:
    response = client.post("/tickets", json={"category": "Printer", "priority": "Low"})
    assert response.status_code == 422


def test_IT_004_post_tickets_rejects_invalid_priority(client: TestClient) -> None:
    response = client.post("/tickets", json={"category": "Account", "priority": "Urgent"})
    assert response.status_code == 422


def test_IT_005_get_tickets_returns_all_tickets(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.get("/tickets")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_IT_006_get_tickets_filters_by_status(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.get("/tickets", params={"status": "In Progress"})
    assert response.status_code == 200
    assert all(item["status"] == "In Progress" for item in response.json())


def test_IT_007_get_tickets_returns_empty_array_when_no_match(client: TestClient) -> None:
    ticket_service.replace_tickets(
        [
            Ticket(id="TKT-001", category=TicketCategory.HARDWARE, priority=TicketPriority.HIGH, status=TicketStatus.OPEN),
            Ticket(
                id="TKT-002",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.IN_PROGRESS,
            ),
        ]
    )
    response = client.get("/tickets", params={"status": "Resolved"})
    assert response.status_code == 200
    assert response.json() == []


def test_IT_008_get_ticket_by_id_returns_matching_ticket(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.get("/tickets/TKT-001")
    assert response.status_code == 200


def test_IT_009_get_ticket_by_id_returns_404_when_not_found(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.get("/tickets/TKT-999")
    assert response.status_code == 404


def test_IT_010_get_ticket_by_id_rejects_invalid_id_format(client: TestClient) -> None:
    response = client.get("/tickets/TK-001")
    assert response.status_code == 422


def test_IT_011_patch_ticket_status_updates_successfully(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.patch("/tickets/TKT-001/status", json={"status": "Resolved"})
    assert response.status_code == 200


def test_IT_012_patch_ticket_status_rejects_invalid_status(client: TestClient) -> None:
    response = client.patch("/tickets/TKT-001/status", json={"status": "Closed"})
    assert response.status_code == 422


def test_IT_013_patch_ticket_status_returns_404_when_ticket_not_found(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.patch("/tickets/TKT-999/status", json={"status": "Open"})
    assert response.status_code == 404


def test_IT_014_get_summary_returns_counts_matching_current_data(client: TestClient) -> None:
    _seed_three_tickets()
    response = client.get("/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["open"] == 1
    assert body["in_progress"] == 1
    assert body["resolved"] == 1


def test_IT_015_summary_reflects_latest_state_after_create_or_update(client: TestClient) -> None:
    _seed_three_tickets()
    first_response = client.get("/summary")
    ticket_service.replace_tickets(
        [
            *ticket_service.snapshot_tickets(),
            Ticket(id="TKT-004", category=TicketCategory.ACCOUNT, priority=TicketPriority.LOW, status=TicketStatus.OPEN),
        ]
    )
    state.ticket_id_counter = 4
    second_response = client.get("/summary")
    assert first_response.json()["total"] == 3
    assert second_response.json()["total"] == 4


def test_IT_016_seed_enabled_app_starts_with_three_tickets_across_three_statuses() -> None:
    seeded_client = TestClient(create_app(seed_data_enabled=True))
    response = seeded_client.get("/tickets")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_IT_017_seed_disabled_app_starts_with_empty_state() -> None:
    reset_state(seed_data_enabled=False)
    empty_client = TestClient(create_app(seed_data_enabled=False))
    tickets_response = empty_client.get("/tickets")
    summary_response = empty_client.get("/summary")
    assert tickets_response.json() == []
    assert summary_response.json() == {"total": 0, "open": 0, "in_progress": 0, "resolved": 0}
