from sqlalchemy.orm import Session


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
