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
