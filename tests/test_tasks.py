import copy

import pytest

from app import app
from services.tasks import (
    TASKS,
    create_task,
    create_tasks,
    get_task,
    list_tasks,
    process_order,
    update_task_priority,
)
from utils.errors import NotFoundError, ValidationError


@pytest.fixture(autouse=True)
def restore_tasks():
    """Reset TASKS after each test so tests don't affect each other."""
    snapshot = copy.deepcopy(TASKS)
    yield
    TASKS.clear()
    TASKS.update(snapshot)

@pytest.fixture
def client():
    return app.test_client()


def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(NotFoundError):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(NotFoundError):
        get_task(999)

def test_list_tasks_by_user():
    result = list_tasks(user_id=2)
    assert [task["id"] for task in result] == [3]

def test_list_tasks_unknown_user():
    with pytest.raises(NotFoundError):
        list_tasks(user_id=999)

def test_list_tasks_by_user_and_priority():
    update_task_priority(2, 1)
    assert [task["id"] for task in list_tasks(user_id=1, priority=1)] == [2]
    assert list_tasks(user_id=2, priority=1) == []

def test_create_task_default_priority():
    result = create_task("New task", 1)
    assert result["priority"] == 3

def test_create_task_with_priority():
    result = create_task("Urgent task", 1, priority=5)
    assert result["priority"] == 5

@pytest.mark.parametrize("priority", [0, 6, "3", True])
def test_create_task_invalid_priority(priority):
    with pytest.raises(ValidationError):
        create_task("Bad task", 1, priority=priority)

def test_list_tasks_all():
    result = list_tasks()
    assert [task["id"] for task in result] == [1, 2, 3]

def test_list_tasks_filtered():
    create_task("Urgent task", 1, priority=5)
    result = list_tasks(priority=5)
    assert [task["title"] for task in result] == ["Urgent task"]

def test_list_tasks_invalid_priority():
    with pytest.raises(ValidationError):
        list_tasks(priority=9)

def test_update_task_priority_valid():
    result = update_task_priority(2, 1)
    assert result["priority"] == 1
    assert get_task(2)["priority"] == 1

@pytest.mark.parametrize("priority", [0, 6])
def test_update_task_priority_invalid(priority):
    with pytest.raises(ValidationError):
        update_task_priority(2, priority)

def test_update_task_priority_not_found():
    with pytest.raises(NotFoundError):
        update_task_priority(999, 2)

def test_post_task_with_priority(client):
    response = client.post("/api/tasks",
                           json={"title": "x", "user_id": 1, "priority": 4})
    assert response.status_code == 201
    assert response.get_json()["priority"] == 4

def test_post_task_default_priority(client):
    response = client.post("/api/tasks", json={"title": "x", "user_id": 1})
    assert response.status_code == 201
    assert response.get_json()["priority"] == 3

def test_post_task_invalid_priority(client):
    response = client.post("/api/tasks",
                           json={"title": "x", "user_id": 1, "priority": 7})
    assert response.status_code == 422

def test_post_task_null_priority(client):
    response = client.post("/api/tasks",
                           json={"title": "x", "user_id": 1, "priority": None})
    assert response.status_code == 422

@pytest.mark.parametrize("priority", [0, False, "3"])
def test_post_task_invalid_priority_types(client, priority):
    response = client.post("/api/tasks",
                           json={"title": "x", "user_id": 1,
                                 "priority": priority})
    assert response.status_code == 422

def test_post_task_missing_title(client):
    response = client.post("/api/tasks", json={"user_id": 1})
    assert response.status_code == 422

def test_get_tasks_filtered_by_priority(client):
    update_task_priority(1, 2)
    response = client.get("/api/tasks?priority=2")
    assert response.status_code == 200
    assert [task["id"] for task in response.get_json()] == [1]

def test_get_tasks_sorted_by_priority(client):
    update_task_priority(1, 5)
    update_task_priority(3, 1)
    create_task("Also urgent", 1, priority=1)
    response = client.get("/api/tasks")
    assert [task["id"] for task in response.get_json()] == [3, 4, 2, 1]

@pytest.mark.parametrize("value", ["abc", "2.5", ""])
def test_get_tasks_non_numeric_priority(client, value):
    response = client.get(f"/api/tasks?priority={value}")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid priority: must be a whole number"

def test_get_tasks_out_of_range_priority(client):
    response = client.get("/api/tasks?priority=9")
    assert response.status_code == 422

def test_get_task_includes_priority(client):
    response = client.get("/api/tasks/1")
    assert response.get_json()["priority"] == 3

def test_patch_task_priority(client):
    response = client.patch("/api/tasks/2", json={"priority": 1})
    assert response.status_code == 200
    assert response.get_json()["priority"] == 1

def test_patch_task_invalid_priority(client):
    response = client.patch("/api/tasks/2", json={"priority": 9})
    assert response.status_code == 422

def test_patch_task_not_found(client):
    response = client.patch("/api/tasks/999", json={"priority": 2})
    assert response.status_code == 404

def test_patch_task_missing_priority(client):
    response = client.patch("/api/tasks/2", json={})
    assert response.status_code == 422

def test_patch_task_null_priority(client):
    response = client.patch("/api/tasks/2", json={"priority": None})
    assert response.status_code == 422
    assert get_task(2)["priority"] == 3

def test_all_endpoints_return_priority(client):
    created = client.post("/api/tasks",
                          json={"title": "x", "user_id": 1, "priority": 4})
    task_id = created.get_json()["id"]
    assert created.get_json()["priority"] == 4

    patched = client.patch(f"/api/tasks/{task_id}", json={"priority": 2})
    assert patched.get_json()["priority"] == 2

    single = client.get(f"/api/tasks/{task_id}")
    assert single.get_json()["priority"] == 2

    listed = client.get("/api/tasks").get_json()
    assert all("priority" in task for task in listed)
    assert next(t for t in listed if t["id"] == task_id)["priority"] == 2

def test_create_tasks_valid():
    result = create_tasks([{"title": "a", "user_id": 1, "priority": 5},
                           {"title": "b", "user_id": 2}])
    assert [task["title"] for task in result] == ["a", "b"]
    assert [task["id"] for task in result] == [4, 5]
    assert [task["priority"] for task in result] == [5, 3]

def test_create_tasks_rejects_whole_batch():
    with pytest.raises(ValidationError, match=r"^Item 1: Invalid priority"):
        create_tasks([{"title": "a", "user_id": 1},
                      {"title": "b", "user_id": 1, "priority": 9}])
    assert len(TASKS) == 3

def test_create_tasks_missing_title():
    with pytest.raises(ValidationError, match=r"^Item 0: Invalid title"):
        create_tasks([{"user_id": 1}])
    assert len(TASKS) == 3

def test_post_bulk_valid(client):
    response = client.post("/api/tasks/bulk",
                           json=[{"title": "a", "user_id": 1, "priority": 2},
                                 {"title": "b", "user_id": 2}])
    assert response.status_code == 201
    tasks = response.get_json()
    assert [task["title"] for task in tasks] == ["a", "b"]
    assert [task["priority"] for task in tasks] == [2, 3]

def test_post_bulk_invalid_item_creates_nothing(client):
    response = client.post("/api/tasks/bulk",
                           json=[{"title": "a", "user_id": 1},
                                 {"title": "", "user_id": 1}])
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Item 1:")
    assert len(client.get("/api/tasks").get_json()) == 3

def test_post_bulk_unknown_user_creates_nothing(client):
    response = client.post("/api/tasks/bulk",
                           json=[{"title": "a", "user_id": 1},
                                 {"title": "b", "user_id": 999}])
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item 1: User not found"
    assert len(TASKS) == 3

def test_post_bulk_null_item(client):
    response = client.post("/api/tasks/bulk", json=[None])
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Item 0:")

def test_post_bulk_null_priority(client):
    response = client.post("/api/tasks/bulk",
                           json=[{"title": "a", "user_id": 1,
                                  "priority": None}])
    assert response.status_code == 422
    assert len(TASKS) == 3

@pytest.mark.parametrize("body", [{"title": "a", "user_id": 1}, []])
def test_post_bulk_body_not_non_empty_list(client, body):
    response = client.post("/api/tasks/bulk", json=body)
    assert response.status_code == 422
