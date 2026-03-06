# tests/security/test_authorization.py

TASKS_URL = "/api/v1/tasks"


# -------------------------------------------------
# 1. Authentication Required
# -------------------------------------------------

def test_access_without_token_denied(client, user_task):
    response = client.get(f"{TASKS_URL}/{user_task.id}")
    assert response.status_code in (401, 403)


# -------------------------------------------------
# 2. Resource Ownership – Read
# -------------------------------------------------

def test_user_can_access_own_task(client, user_headers, user_task):
    response = client.get(
        f"{TASKS_URL}/{user_task.id}",
        headers=user_headers,
    )
    assert response.status_code == 200


def test_user_cannot_access_other_user_task(
    client,
    user_headers,
    other_user_task,
):
    response = client.get(
        f"{TASKS_URL}/{other_user_task.id}",
        headers=user_headers,
    )
    assert response.status_code in (403, 404)


# -------------------------------------------------
# 3. Create Permissions
# -------------------------------------------------

def test_user_can_create_task(client, user_headers):
    payload = {
        "title": "My Task",
        "description": "Test task",
    }

    response = client.post(
        TASKS_URL,
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]


# -------------------------------------------------
# 4. Update Permissions
# -------------------------------------------------

def test_user_can_update_own_task(
    client,
    user_headers,
    user_task,
):
    payload = {
        "title": "Updated title"
    }

    response = client.put(
        f"{TASKS_URL}/{user_task.id}",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == payload["title"]


def test_user_cannot_update_other_user_task(
    client,
    user_headers,
    other_user_task,
):
    payload = {
        "title": "Hacked title"
    }

    response = client.put(
        f"{TASKS_URL}/{other_user_task.id}",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code in (403, 404)


# -------------------------------------------------
# 5. Delete Permissions
# -------------------------------------------------

def test_user_can_delete_own_task(
    client,
    user_headers,
    user_task,
):
    response = client.delete(
        f"{TASKS_URL}/{user_task.id}",
        headers=user_headers,
    )

    assert response.status_code in (200, 204)


def test_user_cannot_delete_other_user_task(
    client,
    user_headers,
    other_user_task,
):
    response = client.delete(
        f"{TASKS_URL}/{other_user_task.id}",
        headers=user_headers,
    )

    assert response.status_code in (403, 404)


# -------------------------------------------------
# 6. ID Manipulation (Horizontal Privilege Escalation)
# -------------------------------------------------

def test_id_manipulation_denied(
    client,
    user_headers,
    other_user_task,
):
    manipulated_id = other_user_task.id + 9999

    response = client.get(
        f"{TASKS_URL}/{manipulated_id}",
        headers=user_headers,
    )

    assert response.status_code in (403, 404)