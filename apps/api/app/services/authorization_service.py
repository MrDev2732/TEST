from collections.abc import Mapping

ROLE_ID_BY_NAME: Mapping[str, int] = {
    "seller": 1,
    "branch_admin": 2,
    "tenant_admin": 3,
    "platform_admin": 4,
}

ALLOWED_ROLE_ASSIGNMENTS: Mapping[str, set[int]] = {
    "platform_admin": set(ROLE_ID_BY_NAME.values()),
    "tenant_admin": {
        ROLE_ID_BY_NAME["seller"],
        ROLE_ID_BY_NAME["branch_admin"],
        ROLE_ID_BY_NAME["tenant_admin"],
    },
}


def validate_role_assignment(actor_role: str, target_role_id: int) -> bool:
    allowed_roles = ALLOWED_ROLE_ASSIGNMENTS.get(actor_role)
    if not allowed_roles:
        return False
    return target_role_id in allowed_roles
