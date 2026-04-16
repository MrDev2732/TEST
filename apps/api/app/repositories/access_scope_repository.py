from sqlalchemy.orm import Session

from app.models.models import Branch, User, UserBranchAssignment


class AccessScopeRepository:
    def get_assigned_branch_ids(self, db: Session, user_id: int) -> list[int]:
        rows = (
            db.query(UserBranchAssignment.branch_id)
            .join(Branch, Branch.id == UserBranchAssignment.branch_id)
            .join(User, User.id == UserBranchAssignment.user_id)
            .filter(UserBranchAssignment.user_id == user_id)
            .filter(User.tenant_id == Branch.tenant_id)
            .order_by(UserBranchAssignment.branch_id)
            .all()
        )
        return [branch_id for (branch_id,) in rows]

    def list_users_in_branches(self, db: Session, branch_ids: list[int]):
        if not branch_ids:
            return []
        return (
            db.query(User)
            .join(UserBranchAssignment, UserBranchAssignment.user_id == User.id)
            .join(Branch, Branch.id == UserBranchAssignment.branch_id)
            .filter(User.tenant_id == Branch.tenant_id)
            .filter(UserBranchAssignment.branch_id.in_(branch_ids))
            .distinct()
            .order_by(User.id)
            .all()
        )

    def user_in_branches(self, db: Session, user_id: int, branch_ids: list[int]) -> bool:
        if not branch_ids:
            return False
        return (
            db.query(User.id)
            .join(UserBranchAssignment, UserBranchAssignment.user_id == User.id)
            .join(Branch, Branch.id == UserBranchAssignment.branch_id)
            .filter(User.id == user_id, UserBranchAssignment.branch_id.in_(branch_ids), User.tenant_id == Branch.tenant_id)
            .first()
            is not None
        )
