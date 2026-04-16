import pytest

ACTORS = {
    "seller": "seller@t1.example.com",
    "branch_admin": "branch@t1.example.com",
    "tenant_admin": "tenant@t1.example.com",
    "platform_admin": "platform@test.com",
}


@pytest.mark.parametrize(
    ("actor", "method", "path", "payload", "expected_status"),
    [
        ("seller", "get", "/tenants", None, 403),
        ("branch_admin", "get", "/tenants", None, 403),
        ("tenant_admin", "get", "/tenants", None, 200),
        ("platform_admin", "get", "/tenants", None, 200),
        (
            "tenant_admin",
            "post",
            "/tenants",
            {"name": "Created by tenant", "slug": "by-tenant", "status": "active"},
            403,
        ),
        (
            "platform_admin",
            "post",
            "/tenants",
            {"name": "Created by platform", "slug": "by-platform", "status": "active"},
            200,
        ),
        ("tenant_admin", "get", "/tenants/2", None, 403),
        ("platform_admin", "get", "/tenants/2", None, 200),
        (
            "seller",
            "post",
            "/branches",
            {"tenant_id": 1, "name": "Nueva", "code": "NUEVA", "status": "active"},
            403,
        ),
        (
            "tenant_admin",
            "post",
            "/branches",
            {"tenant_id": 2, "name": "Cross", "code": "XBR", "status": "active"},
            403,
        ),
        (
            "tenant_admin",
            "post",
            "/branches",
            {"tenant_id": 1, "name": "Tenant branch", "code": "TB1", "status": "active"},
            200,
        ),
        ("seller", "get", "/branches/2", None, 403),
        ("branch_admin", "get", "/branches/3", None, 403),
        ("platform_admin", "get", "/branches/2", None, 200),
        ("seller", "get", "/users", None, 403),
        ("branch_admin", "get", "/users", None, 200),
        ("branch_admin", "get", "/users/7", None, 403),
        ("tenant_admin", "get", "/users/5", None, 403),
        ("platform_admin", "get", "/users/5", None, 200),
        (
            "tenant_admin",
            "post",
            "/users",
            {
                "tenant_id": 2,
                "email": "new-user@test.com",
                "full_name": "New User",
                "status": "active",
                "role_id": 1,
                "default_branch_id": 1,
                "password": "Pass1234!",
            },
            200,
        ),
    ],
)
def test_authorization_matrix(client, auth_headers, actor, method, path, payload, expected_status):
    response = client.request(method, path, headers=auth_headers(ACTORS[actor]), json=payload)
    assert response.status_code == expected_status
