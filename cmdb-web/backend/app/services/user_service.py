"""用户服务层"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
    UnauthorizedException,
)
from app.models.user import User, Role, UserStatus
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """用户服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[UserStatus] = None,
    ) -> List[User]:
        """获取用户列表"""
        query = self.db.query(User)
        if status:
            query = query.filter(User.status == status)
        return query.offset(skip).limit(limit).all()

    def get_count(self) -> int:
        """获取用户总数"""
        return self.db.query(User).count()

    def create(self, user_in: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.get_by_username(user_in.username)
        if existing_user:
            raise ConflictException(message="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = self.get_by_email(user_in.email)
        if existing_email:
            raise ConflictException(message="邮箱已被使用")

        # 创建用户
        db_obj = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            password_hash=hash_password(user_in.password),
            status=UserStatus.ACTIVE,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, user_id: int, user_in: UserUpdate) -> User:
        """更新用户"""
        db_obj = self.get_by_id(user_id)
        if not db_obj:
            raise NotFoundException(message="用户不存在")

        # 检查邮箱是否被其他用户使用
        if user_in.email:
            existing_email = self.get_by_email(user_in.email)
            if existing_email and existing_email.id != user_id:
                raise ConflictException(message="邮箱已被其他用户使用")

        # 更新密码
        if user_in.password:
            user_in.password_hash = hash_password(user_in.password)
            del user_in.password

        return self._update_db_obj(db_obj, user_in)

    def delete(self, user_id: int) -> User:
        """删除用户"""
        db_obj = self.get_by_id(user_id)
        if not db_obj:
            raise NotFoundException(message="用户不存在")

        self.db.delete(db_obj)
        self.db.commit()
        return db_obj

    def update_status(self, user_id: int, status: UserStatus) -> User:
        """更新用户状态"""
        db_obj = self.get_by_id(user_id)
        if not db_obj:
            raise NotFoundException(message="用户不存在")

        db_obj.status = status
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return verify_password(plain_password, hashed_password)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if user.status != UserStatus.ACTIVE:
            raise BadRequestException(message="用户账号已被禁用")
        return user

    def assign_role(self, user_id: int, role_id: int) -> User:
        """为用户分配角色"""
        db_obj = self.get_by_id(user_id)
        if not db_obj:
            raise NotFoundException(message="用户不存在")

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise NotFoundException(message="角色不存在")

        if role not in db_obj.roles:
            db_obj.roles.append(role)
            self.db.commit()
            self.db.refresh(db_obj)

        return db_obj

    def remove_role(self, user_id: int, role_id: int) -> User:
        """移除用户角色"""
        db_obj = self.get_by_id(user_id)
        if not db_obj:
            raise NotFoundException(message="用户不存在")

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise NotFoundException(message="角色不存在")

        if role in db_obj.roles:
            db_obj.roles.remove(role)
            self.db.commit()
            self.db.refresh(db_obj)

        return db_obj

    def _update_db_obj(self, db_obj: User, user_in: UserUpdate) -> User:
        """更新数据库对象"""
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
