"""API 路由"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.ci import (
    CICreate,
    CIUpdate,
    CIResponse,
    CIListResponse,
    CIRelationCreate,
    CIRelationResponse,
    CISearchRequest,
)
from app.schemas.common import PaginatedResponse
from app.services.ci_service import CIService
from app.models.ci import CIType, CIStatus
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CIResponse])
def list_cis(
    db: Session = Depends(get_db),
    ci_type: Optional[CIType] = Query(None, description="配置项类型"),
    status: Optional[CIStatus] = Query(None, description="状态"),
    environment: Optional[str] = Query(None, description="环境"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
):
    """获取配置项列表"""
    service = CIService(db)
    skip = (page - 1) * page_size

    items = service.get_multi(
        skip=skip,
        limit=page_size,
        ci_type=ci_type,
        status=status,
        environment=environment,
    )
    total = service.get_count(ci_type=ci_type, status=status, environment=environment)

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CIResponse, status_code=status.HTTP_201_CREATED)
def create_ci(
    ci_in: CICreate,
    db: Session = Depends(get_db),
):
    """创建配置项"""
    service = CIService(db)
    # 提取具体类型的字段，排除 CICreate 中已有的基础字段
    base_fields = {"name", "code", "description", "status", "environment", "owner", "tags", "ci_type"}
    ci_data = ci_in.model_dump()
    details = {k: v for k, v in ci_data.items() if k not in base_fields and v is not None}

    return service.create(ci_in=ci_in, ci_details=details)


@router.get("/{ci_id}", response_model=CIResponse)
def get_ci(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """获取配置项详情"""
    service = CIService(db)
    ci = service.get_by_id(ci_id)
    if not ci:
        raise NotFoundException(message="配置项不存在")
    return ci


@router.put("/{ci_id}", response_model=CIResponse)
def update_ci(
    ci_id: int,
    ci_in: CIUpdate,
    db: Session = Depends(get_db),
):
    """更新配置项"""
    service = CIService(db)
    return service.update(ci_id=ci_id, ci_in=ci_in)


@router.delete("/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ci(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """删除配置项"""
    service = CIService(db)
    service.delete(ci_id=ci_id)


@router.post("/{ci_id}/relations", response_model=CIRelationResponse)
def create_relation(
    ci_id: int,
    relation_in: CIRelationCreate,
    db: Session = Depends(get_db),
):
    """创建配置项关系"""
    service = CIService(db)
    # 强制设置源配置项为当前 ci_id
    relation_data = relation_in.model_dump()
    relation_data["source_ci_id"] = ci_id
    relation_update = CIRelationCreate(**relation_data)
    return service.create_relation(relation_in=relation_update)


@router.get("/{ci_id}/relations", response_model=List[CIRelationResponse])
def get_relations(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """获取配置项的所有关系"""
    service = CIService(db)
    return service.get_relations(ci_id=ci_id)


@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(
    relation_id: int,
    db: Session = Depends(get_db),
):
    """删除配置项关系"""
    service = CIService(db)
    service.delete_relation(relation_id=relation_id)


@router.post("/search", response_model=PaginatedResponse[CIResponse])
def search_cis(
    search_request: CISearchRequest,
    db: Session = Depends(get_db),
):
    """搜索配置项"""
    service = CIService(db)
    skip = (search_request.page - 1) * search_request.page_size

    items, total = service.search(
        ci_type=search_request.ci_type,
        name=search_request.name,
        code=search_request.code,
        status=search_request.status,
        environment=search_request.environment,
        owner=search_request.owner,
        skip=skip,
        limit=search_request.page_size,
    )

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
    )
