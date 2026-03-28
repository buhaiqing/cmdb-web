"""配置项服务层"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.ci import (
    ConfigurationItem,
    ConfigurationItemRelation,
    CIType,
    CIStatus,
    Server,
    NetworkDevice,
    Database,
    Middleware,
    Application,
    Container,
    K8sResource,
    CloudResource,
)
from app.models.change import ChangeRecord, ChangeType, ChangeStatus, ChangePriority
from app.schemas.ci import CICreate, CIUpdate, CIRelationCreate


class CIService:
    """配置项服务类"""

    # CI 类型与具体模型的映射
    CI_MODEL_MAP = {
        CIType.SERVER: Server,
        CIType.NETWORK_DEVICE: NetworkDevice,
        CIType.DATABASE: Database,
        CIType.MIDDLEWARE: Middleware,
        CIType.APPLICATION: Application,
        CIType.CONTAINER: Container,
        CIType.K8S_RESOURCE: K8sResource,
        CIType.CLOUD_RESOURCE: CloudResource,
    }

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ci_id: int) -> Optional[ConfigurationItem]:
        """根据 ID 获取配置项"""
        return (
            self.db.query(ConfigurationItem)
            .options(
                joinedload(ConfigurationItem.relations),
                joinedload(ConfigurationItem.target_relations),
            )
            .filter(ConfigurationItem.id == ci_id)
            .first()
        )

    def get_by_code(self, code: str) -> Optional[ConfigurationItem]:
        """根据代码获取配置项"""
        return self.db.query(ConfigurationItem).filter(ConfigurationItem.code == code).first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        ci_type: Optional[CIType] = None,
        status: Optional[CIStatus] = None,
        environment: Optional[str] = None,
    ) -> List[ConfigurationItem]:
        """获取配置项列表"""
        query = self.db.query(ConfigurationItem)
        if ci_type:
            query = query.filter(ConfigurationItem.ci_type == ci_type)
        if status:
            query = query.filter(ConfigurationItem.status == status)
        if environment:
            query = query.filter(ConfigurationItem.environment == environment)
        return query.offset(skip).limit(limit).all()

    def get_count(
        self,
        ci_type: Optional[CIType] = None,
        status: Optional[CIStatus] = None,
        environment: Optional[str] = None,
    ) -> int:
        """获取配置项总数"""
        query = self.db.query(ConfigurationItem)
        if ci_type:
            query = query.filter(ConfigurationItem.ci_type == ci_type)
        if status:
            query = query.filter(ConfigurationItem.status == status)
        if environment:
            query = query.filter(ConfigurationItem.environment == environment)
        return query.count()

    def search(
        self,
        *,
        ci_type: Optional[CIType] = None,
        name: Optional[str] = None,
        code: Optional[str] = None,
        status: Optional[CIStatus] = None,
        environment: Optional[str] = None,
        owner: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[ConfigurationItem], int]:
        """搜索配置项"""
        query = self.db.query(ConfigurationItem)

        # 构建查询条件
        conditions = []
        if ci_type:
            conditions.append(ConfigurationItem.ci_type == ci_type)
        if name:
            conditions.append(ConfigurationItem.name.ilike(f"%{name}%"))
        if code:
            conditions.append(ConfigurationItem.code.ilike(f"%{code}%"))
        if status:
            conditions.append(ConfigurationItem.status == status)
        if environment:
            conditions.append(ConfigurationItem.environment == environment)
        if owner:
            conditions.append(ConfigurationItem.owner.ilike(f"%{owner}%"))

        if conditions:
            query = query.filter(and_(*conditions))

        # 获取总数
        total = query.count()

        # 分页
        items = query.offset(skip).limit(limit).all()

        return items, total

    def create(self, ci_in: CICreate, ci_details: Dict[str, Any]) -> ConfigurationItem:
        """创建配置项"""
        # 检查代码是否已存在
        existing = self.get_by_code(ci_in.code)
        if existing:
            raise ConflictException(message="配置项代码已存在")

        # 创建配置项
        db_obj = ConfigurationItem(
            ci_type=ci_in.ci_type,
            name=ci_in.name,
            code=ci_in.code,
            description=ci_in.description,
            status=ci_in.status,
            environment=ci_in.environment,
            owner=ci_in.owner,
            tags=json.dumps(ci_in.tags) if ci_in.tags else None,
        )
        self.db.add(db_obj)
        self.db.flush()  # 获取 ID

        # 创建具体类型的记录
        model_class = self.CI_MODEL_MAP.get(ci_in.ci_type)
        if not model_class:
            raise BadRequestException(message="无效的配置项类型")

        details_obj = model_class(id=db_obj.id, **ci_details)
        self.db.add(details_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        # 创建变更记录
        self._create_change_record(
            ci_id=db_obj.id,
            change_type=ChangeType.CREATE,
            title=f"创建配置项：{ci_in.name}",
            new_value=ci_in.model_dump() | ci_details,
        )

        return db_obj

    def update(
        self, ci_id: int, ci_in: CIUpdate, ci_details: Optional[Dict[str, Any]] = None
    ) -> ConfigurationItem:
        """更新配置项"""
        db_obj = self.get_by_id(ci_id)
        if not db_obj:
            raise NotFoundException(message="配置项不存在")

        # 记录旧值
        old_value = db_obj.to_dict()

        # 更新配置项
        update_data = ci_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # 更新具体类型的记录
        if ci_details:
            model_class = self.CI_MODEL_MAP.get(db_obj.ci_type)
            if model_class:
                details_obj = (
                    self.db.query(model_class).filter(model_class.id == ci_id).first()
                )
                if details_obj:
                    for field, value in ci_details.items():
                        setattr(details_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)

        # 创建变更记录
        self._create_change_record(
            ci_id=ci_id,
            change_type=ChangeType.UPDATE,
            title=f"更新配置项：{db_obj.name}",
            old_value=old_value,
            new_value=ci_in.model_dump() | (ci_details or {}),
        )

        return db_obj

    def delete(self, ci_id: int) -> ConfigurationItem:
        """删除配置项"""
        db_obj = self.get_by_id(ci_id)
        if not db_obj:
            raise NotFoundException(message="配置项不存在")

        # 记录旧值
        old_value = db_obj.to_dict()

        # 删除关联关系
        self.db.query(ConfigurationItemRelation).filter(
            or_(
                ConfigurationItemRelation.source_ci_id == ci_id,
                ConfigurationItemRelation.target_ci_id == ci_id,
            )
        ).delete(synchronize_session=False)

        # 删除具体类型的记录
        model_class = self.CI_MODEL_MAP.get(db_obj.ci_type)
        if model_class:
            self.db.query(model_class).filter(model_class.id == ci_id).delete()

        # 删除配置项
        self.db.delete(db_obj)
        self.db.commit()

        # 创建变更记录
        self._create_change_record(
            ci_id=ci_id,
            change_type=ChangeType.DELETE,
            title=f"删除配置项：{db_obj.name}",
            old_value=old_value,
        )

        return db_obj

    def create_relation(self, relation_in: CIRelationCreate) -> ConfigurationItemRelation:
        """创建配置项关系"""
        # 检查源和目标配置项是否存在
        source_ci = self.get_by_id(relation_in.source_ci_id)
        if not source_ci:
            raise NotFoundException(message="源配置项不存在")

        target_ci = self.get_by_id(relation_in.target_ci_id)
        if not target_ci:
            raise NotFoundException(message="目标配置项不存在")

        # 检查关系是否已存在
        existing = (
            self.db.query(ConfigurationItemRelation)
            .filter(
                and_(
                    ConfigurationItemRelation.source_ci_id == relation_in.source_ci_id,
                    ConfigurationItemRelation.target_ci_id == relation_in.target_ci_id,
                    ConfigurationItemRelation.relation_type == relation_in.relation_type,
                )
            )
            .first()
        )
        if existing:
            raise ConflictException(message="关系已存在")

        # 创建关系
        db_obj = ConfigurationItemRelation(
            source_ci_id=relation_in.source_ci_id,
            target_ci_id=relation_in.target_ci_id,
            relation_type=relation_in.relation_type,
            description=relation_in.description,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def delete_relation(self, relation_id: int) -> ConfigurationItemRelation:
        """删除配置项关系"""
        db_obj = self.db.query(ConfigurationItemRelation).filter(
            ConfigurationItemRelation.id == relation_id
        ).first()
        if not db_obj:
            raise NotFoundException(message="关系不存在")

        self.db.delete(db_obj)
        self.db.commit()
        return db_obj

    def get_relations(self, ci_id: int) -> List[ConfigurationItemRelation]:
        """获取配置项的所有关系"""
        ci = self.get_by_id(ci_id)
        if not ci:
            raise NotFoundException(message="配置项不存在")

        return ci.relations + ci.target_relations

    def _create_change_record(
        self,
        ci_id: int,
        change_type: ChangeType,
        title: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
    ) -> ChangeRecord:
        """创建变更记录"""
        db_obj = ChangeRecord(
            ci_id=ci_id,
            change_type=change_type,
            status=ChangeStatus.COMPLETED,
            priority=ChangePriority.MEDIUM,
            title=title,
            old_value=json.dumps(old_value) if old_value else None,
            new_value=json.dumps(new_value) if new_value else None,
        )
        self.db.add(db_obj)
        self.db.commit()
        return db_obj
