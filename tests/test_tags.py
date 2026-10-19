import copy

import pytest

from app import app
from services.tags import TAGS


@pytest.fixture(autouse=True)
def restore_tags():
    """Reset TAGS after each test so tests don't affect each other."""
    snapshot = copy.deepcopy(TAGS)
    yield
    TAGS.clear()
    TAGS.update(snapshot)

@pytest.fixture
def client():
    return app.test_client()


def test_create_tag(client):
    response = client.post("/api/tags", json={"name": "urgent", "color": "red"})
    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "name": "urgent", "color": "red"}
