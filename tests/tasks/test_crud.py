import pytest
from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_create_task_as_user(client, user_headers):
    """
    GIVEN authenticated normal user
    WHEN user creates a task
    THEN task is created successfully
    """

    payload = {
        "title": "My First Task",
        "description": "Testing create task",
    }

    response = client.post(
        TASKS_URL,
        json=payload,
        headers=user_headers,
    )

    # ✅ HTTP status
    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    # ✅ Response structure
    assert "id" in body
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]

    # ✅ Ownership
    assert body["owner_id"] is not None

import pytest
from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_create_task_as_user(client, user_headers):
    """
    GIVEN authenticated normal user
    WHEN user creates a task
    THEN task is created successfully
    """

    payload = {
        "title": "My First Task",
        "description": "Testing create task",
    }

    response = client.post(
        TASKS_URL,
        json=payload,
        headers=user_headers,
    )

    # ✅ HTTP status
    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    # ✅ Response structure
    assert "id" in body
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]

    # ✅ Ownership
    assert body["owner_id"] is not None

from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_get_task_by_id_as_owner(
    client,
    user_headers,
    user_task,
):
    """
    GIVEN authenticated user
    AND user owns a task
    WHEN user requests task by id
    THEN task is returned successfully
    """

    response = client.get(
        f"{TASKS_URL}/{user_task.id}",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == user_task.id
    assert body["title"] == user_task.title
    assert body["description"] == user_task.description

from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_get_task_by_id_not_owner(
    client,
    user_headers,
    other_user_task,
):
    """
    GIVEN authenticated user
    AND task belongs to another user
    WHEN user requests task by id
    THEN access is denied
    """

    response = client.get(
        f"{TASKS_URL}/{other_user_task.id}",
        headers=user_headers,
    )

    # Important security behavior:
    # We return 404 to avoid resource enumeration (IDOR)
    assert response.status_code == status.HTTP_404_NOT_FOUND

from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_update_task_owner(
    client,
    user_headers,
    user_task,
):
    """
    GIVEN authenticated user
    AND user owns the task
    WHEN user updates the task
    THEN task is updated successfully
    """

    payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True,
    }

    response = client.put(
        f"{TASKS_URL}/{user_task.id}",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == user_task.id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True

from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_update_task_not_owner(
    client,
    user_headers,
    other_user_task,
):
    """
    GIVEN authenticated user
    AND task belongs to another user
    WHEN user tries to update the task
    THEN access is denied (task not found)
    """

    payload = {
        "title": "Hacked Title",
        "completed": True,
    }

    response = client.put(
        f"{TASKS_URL}/{other_user_task.id}",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_delete_task_owner(
    client,
    user_headers,
    user_task,
):
    """
    GIVEN authenticated user
    AND task belongs to the user
    WHEN user deletes the task
    THEN task is deleted successfully
    """

    response = client.delete(
        f"{TASKS_URL}/{user_task.id}",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # 🔍 تأكيد إن التاسك اتحذف
    get_response = client.get(
        f"{TASKS_URL}/{user_task.id}",
        headers=user_headers,
    )

    assert get_response.status_code == status.HTTP_404_NOT_FOUND

from fastapi import status

TASKS_URL = "/api/v1/tasks"


def test_delete_task_not_owner(
    client,
    user_headers,
    other_user_task,
):
    """
    GIVEN authenticated user
    AND task belongs to another user
    WHEN user tries to delete the task
    THEN access is denied (task not found)
    """

    response = client.delete(
        f"{TASKS_URL}/{other_user_task.id}",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND        