from collections.abc import Mapping


ROLE_IDS_BY_NAME: Mapping[str, int] = {
    "seller": 1,
    "branch_admin": 2,
    "tenant_admin": 3,
    "platform_admin": 4,
}

ALLOWED_ROLE_IDS_BY_ACTOR: Mapping[str, set[int]] = {
    "platform_admin": {
        ROLE_IDS_BY_NAME["seller"],
        ROLE_IDS_BY_NAME["branch_admin"],
        ROLE_IDS_BY_NAME["tenant_admin"],
        ROLE_IDS_BY_NAME["platform_admin"],
    },
    "tenant_admin": {
        ROLE_IDS_BY_NAME["seller"],
        ROLE_IDS_BY_NAME["branch_admin"],
        ROLE_IDS_BY_NAME["tenant_admin"],
    },
}


def validate_role_assignment(actor_role: str, target_role_id: int) -> bool:
    allowed_role_ids = ALLOWED_ROLE_IDS_BY_ACTOR.get(actor_role)
    if not allowed_role_ids:
        return False
    return target_role_id in allowed_role_ids
