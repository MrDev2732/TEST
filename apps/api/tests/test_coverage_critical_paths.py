from app.core.security import create_access_token


def test_auth_me_rejects_invalid_tokens(client):
    malformed = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert malformed.status_code == 401
    assert malformed.json()["detail"] == "Could not validate credentials"

    missing_sub_token = create_access_token("")
    missing_sub = client.get("/auth/me", headers={"Authorization": f"Bearer {missing_sub_token}"})
    assert missing_sub.status_code == 401
    assert missing_sub.json()["detail"] == "Could not validate credentials"

    unknown_user_token = create_access_token("9999")
    unknown_user = client.get("/auth/me", headers={"Authorization": f"Bearer {unknown_user_token}"})
    assert unknown_user.status_code == 401
    assert unknown_user.json()["detail"] == "Could not validate credentials"


def test_branches_platform_and_patch_paths(client, auth_headers):
    listed = client.get("/branches", headers=auth_headers("platform@test.com"))
    assert listed.status_code == 200
    assert len(listed.json()) >= 2

    not_found = client.patch("/branches/9999", headers=auth_headers("platform@test.com"), json={"name": "x"})
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Not found"

    forbidden = client.patch("/branches/2", headers=auth_headers("branch@t1.example.com"), json={"name": "forbidden"})
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"] == "Forbidden"

    ok = client.patch("/branches/1", headers=auth_headers("branch@t1.example.com"), json={"name": "Updated T1"})
    assert ok.status_code == 200
    assert ok.json()["name"] == "Updated T1"


def test_users_platform_list_and_patch_paths(client, auth_headers):
    listed = client.get("/users", headers=auth_headers("platform@test.com"))
    assert listed.status_code == 200
    assert len(listed.json()) >= 5

    not_found = client.patch("/users/9999", headers=auth_headers("platform@test.com"), json={"full_name": "Nope"})
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Not found"

    forbidden = client.patch("/users/5", headers=auth_headers("tenant@t1.example.com"), json={"full_name": "Nope"})
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"] == "Forbidden"

    tenant_patch = client.patch(
        "/users/3",
        headers=auth_headers("tenant@t1.example.com"),
        json={"full_name": "Tenant Renamed", "tenant_id": 2},
    )
    assert tenant_patch.status_code == 200
    assert tenant_patch.json()["full_name"] == "Tenant Renamed"
    assert tenant_patch.json()["tenant_id"] == 1
