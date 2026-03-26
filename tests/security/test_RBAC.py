"""
RBAC Tests

This file verifies that the RBAC (Role Based Access Control)
system works correctly.

The tests validate that:

1. Authentication is required
2. Users can access their own resources
3. Users cannot access other users resources
4. Permissions are enforced correctly
"""

import pytest


# ---------------------------------------------------------
# 1. Authentication Required
# ---------------------------------------------------------

def test_create_task_requires_authentication(client):
    """
    GIVEN an unauthenticated request
    WHEN creating a task
    THEN API should return 401
    """

    response = client.post(
        "api/v1/tasks",
        json={"title": "Test task"}
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# 2. User Can Create Task
# ---------------------------------------------------------

def test_user_can_create_task(client, user_headers):
    """
    GIVEN authenticated user with CREATE_TASK permission
    WHEN user creates a task
    THEN task should be created
    """

    response = client.post(
        "api/v1/tasks/",
        json={
            "title": "My task",
            "description": "test"
        },
        headers=user_headers
    )
    print(response.status_code)
    print(response.json())
    assert response.status_code == 201
    assert response.json()["title"] == "My task"


# ---------------------------------------------------------
# 3. User Can View Own Task
# ---------------------------------------------------------

def test_user_can_view_own_task(client, user_headers, user_task):
    """
    GIVEN a task owned by the user
    WHEN user requests the task
    THEN API returns the task
    """

    response = client.get(
        f"api/v1/tasks/{user_task.id}",
        headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_task.id


# ---------------------------------------------------------
# 4. User Cannot View Another User Task
# ---------------------------------------------------------

def test_user_cannot_view_other_user_task(
    client,
    user_headers,
    other_user_task
):
    """
    GIVEN a task owned by another user
    WHEN current user requests it
    THEN request should fail
    """

    response = client.get(
        f"api/v1/tasks/{other_user_task.id}",
        headers=user_headers
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# 5. User Can Update Own Task
# ---------------------------------------------------------

def test_user_can_update_own_task(client, user_headers, user_task):
    """
    GIVEN a task owned by user
    WHEN updating the task
    THEN update should succeed
    """

    response = client.put(
        f"api/v1/tasks/{user_task.id}",
        json={"title": "Updated title"},
        headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


# ---------------------------------------------------------
# 6. User Cannot Update Another User Task
# ---------------------------------------------------------

def test_user_cannot_update_other_user_task(
    client,
    user_headers,
    other_user_task
):
    """
    GIVEN task owned by another user
    WHEN update attempted
    THEN request should be forbidden
    """

    response = client.put(
        f"api/v1/tasks/{other_user_task.id}",
        json={"title": "hack"},
        headers=user_headers
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# 7. User Can Delete Own Task
# ---------------------------------------------------------

def test_user_can_delete_own_task(client, user_headers, user_task):
    """
    GIVEN user owns the task
    WHEN deleting task
    THEN deletion succeeds
    """

    response = client.delete(
        f"api/v1/tasks/{user_task.id}",
        headers=user_headers
    )

    assert response.status_code == 204


# ---------------------------------------------------------
# 8. User Cannot Delete Another User Task
# ---------------------------------------------------------

def test_user_cannot_delete_other_user_task(
    client,
    user_headers,
    other_user_task
):
    """
    GIVEN task owned by another user
    WHEN delete attempted
    THEN request should fail
    """

    response = client.delete(
        f"api/v1/tasks/{other_user_task.id}",
        headers=user_headers
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# 9. User Can List Their Own Tasks
# ---------------------------------------------------------

def test_user_can_list_tasks(client, user_headers):
    """
    GIVEN authenticated user
    WHEN requesting task list
    THEN tasks should be returned
    """

    response = client.get(
        "api/v1/tasks/",
        headers=user_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data