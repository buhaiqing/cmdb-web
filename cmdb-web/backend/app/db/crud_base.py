"""CRUD 基础操作"""

from sqlalchemy.orm import Session, Model
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD 基础类"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """根据 ID 获取单条记录"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None,
    ) -> List[ModelType]:
        """获取多条记录"""
        query = db.query(self.model)
        if order_by:
            query = query.order_by(order_by)
        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session) -> int:
        """获取记录总数"""
        return db.query(self.model).count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建记录"""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """更新记录"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """删除记录"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
