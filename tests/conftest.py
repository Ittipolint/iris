from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.backend.main import create_app
from apps.backend.state import reset_state


@pytest.fixture(autouse=True)
def reset_in_memory_store() -> None:
    reset_state(seed_data_enabled=False)
    yield
    reset_state(seed_data_enabled=False)


@pytest.fixture
def app():
    return create_app(seed_data_enabled=False)


@pytest.fixture
def client(app):
    return TestClient(app)
