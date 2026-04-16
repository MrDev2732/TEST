from sqlalchemy import distinct, or_
from sqlalchemy.orm import Session

from app.models.models import Branch, User, UserBranchAssignment


class CRUDRepository:
    def __init__(self, model):
        self.model = model

    def list(self, db: Session, filters: list | None = None):
        query = db.query(self.model)
        if filters:
            for expr in filters:
                query = query.filter(expr)
        return query.order_by(self.model.id).all()

    def get(self, db: Session, entity_id: int):
        return db.query(self.model).filter(self.model.id == entity_id).first()

    def create(self, db: Session, payload: dict):
        entity = self.model(**payload)
        db.add(entity)
        return entity

    def update(self, db: Session, entity, payload: dict):
        for key, value in payload.items():
            setattr(entity, key, value)
        return entity


class AccessScopeRepository:
    def list_branch_ids_for_user(self, db: Session, user_id: int) -> list[int]:
        rows = (
            db.query(UserBranchAssignment.branch_id)
            .filter(UserBranchAssignment.user_id == user_id)
            .order_by(UserBranchAssignment.branch_id)
            .all()
        )
        return [row[0] for row in rows]

    def list_users_for_branch_scope(self, db: Session, branch_ids: list[int]):
        if not branch_ids:
            return []

        return (
            db.query(User)
            .outerjoin(UserBranchAssignment, UserBranchAssignment.user_id == User.id)
            .outerjoin(Branch, Branch.id == UserBranchAssignment.branch_id)
            .filter(
                or_(
                    UserBranchAssignment.branch_id.in_(branch_ids),
                    User.default_branch_id.in_(branch_ids),
                )
            )
            .order_by(User.id)
            .distinct(User.id)
            .all()
        )

    def user_in_branch_scope(self, db: Session, user_id: int, branch_ids: list[int]) -> bool:
        if not branch_ids:
            return False

        row = (
            db.query(distinct(User.id))
            .outerjoin(UserBranchAssignment, UserBranchAssignment.user_id == User.id)
            .outerjoin(Branch, Branch.id == UserBranchAssignment.branch_id)
            .filter(
                User.id == user_id,
                or_(
                    UserBranchAssignment.branch_id.in_(branch_ids),
                    User.default_branch_id.in_(branch_ids),
                ),
            )
            .first()
        )
        return row is not None

    def branch_in_scope(self, db: Session, branch_id: int, branch_ids: list[int]) -> bool:
        if not branch_ids:
            return False

        row = (
            db.query(Branch.id)
            .filter(Branch.id == branch_id, Branch.id.in_(branch_ids))
            .first()
        )
        return row is not None
