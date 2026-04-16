from datetime import datetime


def test_health_contract(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_contract(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_login_and_me_contract(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "tenant@t1.example.com", "password": "Pass1234!"},
    )
    assert login_response.status_code == 200

    token_payload = login_response.json()
    assert token_payload["token_type"] == "bearer"
    assert isinstance(token_payload["access_token"], str)
    assert token_payload["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token_payload['access_token']}"},
    )
    assert me_response.status_code == 200
    me_payload = me_response.json()

    assert set(me_payload.keys()) == {
        "id",
        "email",
        "full_name",
        "role",
        "tenant_id",
        "default_branch_id",
    }
    assert me_payload["email"] == "tenant@t1.example.com"
    assert me_payload["role"] == "tenant_admin"


def test_login_error_contracts(client):
    invalid_password = client.post(
        "/auth/login",
        json={"email": "tenant@t1.example.com", "password": "wrong-password"},
    )
    assert invalid_password.status_code == 401
    assert invalid_password.json()["detail"] == "Invalid credentials"

    inactive_user = client.post(
        "/auth/login",
        json={"email": "seller@t2.example.com", "password": "Pass1234!"},
    )
    assert inactive_user.status_code == 403
    assert inactive_user.json()["detail"] == "User inactive"


def test_user_errors_contract(client, auth_headers):
    not_found = client.get("/users/9999", headers=auth_headers("platform@test.com"))
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Not found"

    forbidden = client.get("/users/5", headers=auth_headers("tenant@t1.example.com"))
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"] == "Forbidden"


def test_list_users_response_shape(client, auth_headers):
    response = client.get("/users", headers=auth_headers("branch@t1.example.com"))
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    first = payload[0]
    expected_keys = {
        "id",
        "auth_provider_user_id",
        "tenant_id",
        "email",
        "full_name",
        "status",
        "role_id",
        "default_branch_id",
        "created_at",
        "updated_at",
    }
    assert set(first.keys()) == expected_keys

    datetime.fromisoformat(first["created_at"])
    datetime.fromisoformat(first["updated_at"])


def test_branch_admin_list_users_is_branch_scoped(client, auth_headers):
    response = client.get("/users", headers=auth_headers("branch@t1.example.com"))
    assert response.status_code == 200
    emails = {item["email"] for item in response.json()}
    assert "seller2@t1.example.com" not in emails


def test_branch_scoped_branch_access(client, auth_headers):
    forbidden_get = client.get("/branches/3", headers=auth_headers("branch@t1.example.com"))
    assert forbidden_get.status_code == 403
    assert forbidden_get.json()["detail"] == "Forbidden"

    forbidden_patch = client.patch(
        "/branches/3",
        headers=auth_headers("branch@t1.example.com"),
        json={"name": "Blocked update"},
    )
    assert forbidden_patch.status_code == 403
    assert forbidden_patch.json()["detail"] == "Forbidden"


def test_login_metrics_requires_platform_admin(client, auth_headers):
    forbidden = client.get("/auth/login/metrics", headers=auth_headers("tenant@t1.example.com"))
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"] == "Insufficient role"

    allowed = client.get("/auth/login/metrics", headers=auth_headers("platform@test.com"))
    assert allowed.status_code == 200
    assert "blocked_ips_count" in allowed.json()


def test_users_list_supports_pagination(client, auth_headers):
    page_1 = client.get("/users?limit=2&offset=0", headers=auth_headers("platform@test.com"))
    page_2 = client.get("/users?limit=2&offset=2", headers=auth_headers("platform@test.com"))

    assert page_1.status_code == 200
    assert page_2.status_code == 200
    assert len(page_1.json()) == 2
    assert len(page_2.json()) == 2
    assert page_1.json()[0]["id"] != page_2.json()[0]["id"]
