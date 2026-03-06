def test_login_rate_limit_blocks_after_multiple_failures(client):
    """
    GIVEN multiple failed login attempts
    WHEN the threshold is exceeded
    THEN login is blocked
    """

    payload = {
        "email": "user@example.com",
        "password": "wrong-password",
    }

    last_response = None

    # نحاول عدد مرات أكبر من المتوقع
    for _ in range(15):
        last_response = client.post(
            "/api/v1/auth/login",
            json=payload,
        )

    # المهم السلوك: block
    assert last_response.status_code in (429, 403)
 
from api.deps.services import get_auth_service
def test_successful_login_does_not_increment_rate_limit(
    client,
    valid_login_payload,
):
    # نفشل شوية
    for _ in range(3):
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "wrong-password",
            },
        )

    # نحاول login ناجح
    response = client.post(
        "/api/v1/auth/login",
        json=valid_login_payload,
    )
    assert response.status_code == 200    