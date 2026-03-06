# tests/performance/test_pagination.py

import pytest


TASKS_URL = "/api/v1/tasks"


@pytest.mark.performance
class TestTasksPagination:
    """
    Pagination & performance tests for tasks listing.
    """

    def test_default_pagination_applied(self, client, user_headers, many_tasks):
        """
        GIVEN a user with many tasks
        WHEN GET /tasks without params
        THEN default limit & offset are applied
        """
        response = client.get(TASKS_URL, headers=user_headers)

        assert response.status_code == 200

        body = response.json()

        assert "items" in body
        assert "limit" in body
        assert "offset" in body
        assert "total" in body

        assert body["offset"] == 0
        assert body["limit"] > 0
        assert len(body["items"]) <= body["limit"]

    def test_valid_limit_is_applied(self, client, user_headers, many_tasks):
        """
        GIVEN a user with many tasks
        WHEN limit is provided
        THEN response contains at most limit items
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": 10},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["limit"] == 10
        assert len(body["items"]) <= 10

    def test_limit_exceeding_max_is_rejected(self, client, user_headers):
        """
        WHEN limit exceeds maximum allowed
        THEN request is rejected
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": 1000},
        )

        assert response.status_code == 422

    def test_negative_limit_is_rejected(self, client, user_headers):
        """
        WHEN limit is negative
        THEN request is rejected
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": -5},
        )

        assert response.status_code == 422

    def test_valid_offset_is_applied(self, client, user_headers, many_tasks):
        """
        GIVEN enough tasks
        WHEN offset is provided
        THEN correct slice is returned
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": 10, "offset": 10},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["offset"] == 10
        assert len(body["items"]) <= 10

    def test_negative_offset_is_rejected(self, client, user_headers):
        """
        WHEN offset is negative
        THEN request is rejected
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"offset": -1},
        )

        assert response.status_code == 422

    def test_total_count_is_independent_of_limit(self, client, user_headers, many_tasks):
        """
        GIVEN many tasks
        WHEN limit is small
        THEN total reflects full dataset size
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": 5},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["total"] >= len(body["items"])
        assert body["limit"] == 5

    def test_user_isolation_with_pagination(
        self, client, user_headers, other_user_headers, many_tasks, other_user_tasks
    ):
        """
        GIVEN multiple users with tasks
        WHEN one user fetches paginated tasks
        THEN only their tasks are returned
        """
        response = client.get(
            TASKS_URL,
            headers=user_headers,
            params={"limit": 20},
        )

        assert response.status_code == 200

        body = response.json()

        for item in body["items"]:
            assert item["owner_id"] == user_headers["user_id"]