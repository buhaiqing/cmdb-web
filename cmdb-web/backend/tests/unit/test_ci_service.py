"""配置项服务层单元测试"""

import pytest
from app.services.ci_service import CIService
from app.models.ci import (
    ConfigurationItem,
    ConfigurationItemRelation,
    CIType,
    CIStatus,
    Server,
)
from app.schemas.ci import CICreate, CIUpdate, CIRelationCreate
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException


class TestCIService:
    """配置项服务测试类"""

    def test_get_by_id_found(self, test_db, sample_ci):
        """测试根据 ID 获取配置项 - 找到"""
        service = CIService(test_db)
        ci = service.get_by_id(sample_ci.id)
        assert ci is not None
        assert ci.id == sample_ci.id

    def test_get_by_id_not_found(self, test_db):
        """测试根据 ID 获取配置项 - 未找到"""
        service = CIService(test_db)
        ci = service.get_by_id(99999)
        assert ci is None

    def test_get_by_code_found(self, test_db, sample_ci):
        """测试根据代码获取配置项 - 找到"""
        service = CIService(test_db)
        ci = service.get_by_code(sample_ci.code)
        assert ci is not None
        assert ci.code == sample_ci.code

    def test_get_by_code_not_found(self, test_db):
        """测试根据代码获取配置项 - 未找到"""
        service = CIService(test_db)
        ci = service.get_by_code("NONEXISTENT")
        assert ci is None

    def test_get_multi_returns_cis(self, test_db, multiple_cis):
        """测试获取多个配置项"""
        service = CIService(test_db)
        cis = service.get_multi(skip=0, limit=10)
        assert len(cis) == 5

    def test_get_multi_with_pagination(self, test_db, multiple_cis):
        """测试分页获取配置项"""
        service = CIService(test_db)
        cis = service.get_multi(skip=0, limit=2)
        assert len(cis) == 2

        cis_page2 = service.get_multi(skip=2, limit=2)
        assert len(cis_page2) == 2

    def test_get_multi_filter_by_ci_type(self, test_db, multiple_cis):
        """测试按类型筛选配置项"""
        service = CIService(test_db)
        cis = service.get_multi(ci_type=CIType.SERVER)
        assert len(cis) == 5

    def test_get_multi_filter_by_status(self, test_db, multiple_cis):
        """测试按状态筛选配置项"""
        service = CIService(test_db)
        cis = service.get_multi(status=CIStatus.ONLINE)
        for ci in cis:
            assert ci.status == CIStatus.ONLINE

    def test_get_multi_filter_by_environment(self, test_db, multiple_cis):
        """测试按环境筛选配置项"""
        service = CIService(test_db)
        cis = service.get_multi(environment="production")
        for ci in cis:
            assert ci.environment == "production"

    def test_get_count_no_filter(self, test_db, multiple_cis):
        """测试获取配置项总数 - 无筛选"""
        service = CIService(test_db)
        count = service.get_count()
        assert count == 5

    def test_get_count_with_filter(self, test_db, multiple_cis):
        """测试获取配置项总数 - 带筛选"""
        service = CIService(test_db)
        count = service.get_count(environment="production")
        assert count == 3

    def test_search_by_name(self, test_db, multiple_cis):
        """测试按名称搜索"""
        service = CIService(test_db)
        results, total = service.search(name="服务器 1")
        assert total >= 1

    def test_search_by_code(self, test_db, multiple_cis):
        """测试按代码搜索"""
        service = CIService(test_db)
        results, total = service.search(code="SERVER-001")
        assert total >= 1

    def test_search_by_environment(self, test_db, multiple_cis):
        """测试按环境搜索"""
        service = CIService(test_db)
        results, total = service.search(environment="production")
        assert total == 3

    def test_search_with_pagination(self, test_db, multiple_cis):
        """测试搜索分页"""
        service = CIService(test_db)
        results, total = service.search(skip=0, limit=2)
        assert len(results) == 2
        assert total == 5

    def test_search_combined_filters(self, test_db, multiple_cis):
        """测试组合条件搜索"""
        service = CIService(test_db)
        results, total = service.search(
            ci_type=CIType.SERVER,
            environment="production",
            status=CIStatus.ONLINE,
        )
        assert total == 3

    def test_create_ci_success(self, test_db):
        """测试创建配置项成功"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.SERVER,
            name="新服务器",
            code="NEW-SERVER-001",
            description="新建的服务器",
            status=CIStatus.ONLINE,
            environment="production",
            owner="admin",
        )
        ci_details = {
            "hostname": "new-server",
            "ip_address": "192.168.1.100",
            "os_type": "Linux",
            "os_version": "Ubuntu 22.04",
            "cpu_cores": 8,
            "memory_gb": 32,
            "disk_gb": 500,
        }
        ci = service.create(ci_in, ci_details)
        assert ci.id is not None
        assert ci.name == "新服务器"
        assert ci.code == "NEW-SERVER-001"

    def test_create_ci_duplicate_code(self, test_db, sample_ci):
        """测试创建配置项 - 代码重复"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.SERVER,
            name="另一个服务器",
            code=sample_ci.code,
            environment="production",
        )
        with pytest.raises(ConflictException) as exc_info:
            service.create(ci_in, {})
        assert "代码已存在" in str(exc_info.value.detail)

    def test_update_ci_success(self, test_db, sample_ci):
        """测试更新配置项成功"""
        service = CIService(test_db)
        ci_in = CIUpdate(
            name="更新的名称",
            description="更新后的描述",
            status=CIStatus.MAINTENANCE,
        )
        ci = service.update(sample_ci.id, ci_in)
        assert ci.name == "更新的名称"
        assert ci.description == "更新后的描述"
        assert ci.status == CIStatus.MAINTENANCE

    def test_update_ci_not_found(self, test_db):
        """测试更新配置项 - 不存在"""
        service = CIService(test_db)
        ci_in = CIUpdate(name="新名称")
        with pytest.raises(NotFoundException):
            service.update(99999, ci_in)

    def test_delete_ci_success(self, test_db, sample_ci):
        """测试删除配置项成功"""
        service = CIService(test_db)
        ci_id = sample_ci.id
        deleted_ci = service.delete(ci_id)
        assert deleted_ci.id == ci_id

        result = service.get_by_id(ci_id)
        assert result is None

    def test_delete_ci_not_found(self, test_db):
        """测试删除配置项 - 不存在"""
        service = CIService(test_db)
        with pytest.raises(NotFoundException):
            service.delete(99999)

    def test_create_relation_success(self, test_db, multiple_cis):
        """测试创建配置项关系成功"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=multiple_cis[0].id,
            target_ci_id=multiple_cis[1].id,
            relation_type="connects_to",
            description="测试连接",
        )
        relation = service.create_relation(relation_in)
        assert relation.id is not None
        assert relation.source_ci_id == multiple_cis[0].id
        assert relation.target_ci_id == multiple_cis[1].id

    def test_create_relation_source_not_found(self, test_db, sample_ci):
        """测试创建关系 - 源配置项不存在"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=99999,
            target_ci_id=sample_ci.id,
            relation_type="connects_to",
        )
        with pytest.raises(NotFoundException) as exc_info:
            service.create_relation(relation_in)
        assert "源配置项不存在" in str(exc_info.value.detail)

    def test_create_relation_target_not_found(self, test_db, sample_ci):
        """测试创建关系 - 目标配置项不存在"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=sample_ci.id,
            target_ci_id=99999,
            relation_type="connects_to",
        )
        with pytest.raises(NotFoundException) as exc_info:
            service.create_relation(relation_in)
        assert "目标配置项不存在" in str(exc_info.value.detail)

    def test_create_relation_duplicate(self, test_db, multiple_cis):
        """测试创建关系 - 关系已存在"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=multiple_cis[0].id,
            target_ci_id=multiple_cis[1].id,
            relation_type="connects_to",
        )
        service.create_relation(relation_in)

        with pytest.raises(ConflictException) as exc_info:
            service.create_relation(relation_in)
        assert "关系已存在" in str(exc_info.value.detail)

    def test_delete_relation_success(self, test_db, multiple_cis):
        """测试删除配置项关系成功"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=multiple_cis[0].id,
            target_ci_id=multiple_cis[1].id,
            relation_type="connects_to",
        )
        relation = service.create_relation(relation_in)
        deleted = service.delete_relation(relation.id)
        assert deleted.id == relation.id

    def test_delete_relation_not_found(self, test_db):
        """测试删除关系 - 不存在"""
        service = CIService(test_db)
        with pytest.raises(NotFoundException):
            service.delete_relation(99999)

    def test_get_relations_success(self, test_db, multiple_cis):
        """测试获取配置项关系"""
        service = CIService(test_db)
        relation_in = CIRelationCreate(
            source_ci_id=multiple_cis[0].id,
            target_ci_id=multiple_cis[1].id,
            relation_type="connects_to",
        )
        service.create_relation(relation_in)

        relations = service.get_relations(multiple_cis[0].id)
        assert len(relations) >= 1

    def test_get_relations_ci_not_found(self, test_db):
        """测试获取关系 - 配置项不存在"""
        service = CIService(test_db)
        with pytest.raises(NotFoundException):
            service.get_relations(99999)


class TestCIServiceCITypes:
    """测试不同 CI 类型的创建"""

    def test_create_server_ci(self, test_db):
        """测试创建服务器类型配置项"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="SERVER-TEST-001",
            environment="production",
        )
        ci_details = {
            "hostname": "test-server",
            "ip_address": "10.0.0.1",
            "os_type": "Linux",
        }
        ci = service.create(ci_in, ci_details)
        assert ci.ci_type == CIType.SERVER

    def test_create_database_ci(self, test_db):
        """测试创建数据库类型配置项"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.DATABASE,
            name="测试数据库",
            code="DB-TEST-001",
            environment="production",
        )
        ci_details = {
            "db_type": "postgresql",
            "version": "15",
            "host": "localhost",
            "port": 5432,
            "database_name": "testdb",
        }
        ci = service.create(ci_in, ci_details)
        assert ci.ci_type == CIType.DATABASE

    def test_create_application_ci(self, test_db):
        """测试创建应用类型配置项"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.APPLICATION,
            name="测试应用",
            code="APP-TEST-001",
            environment="production",
        )
        ci_details = {
            "app_type": "web",
            "language": "python",
            "framework": "fastapi",
            "version": "1.0.0",
        }
        ci = service.create(ci_in, ci_details)
        assert ci.ci_type == CIType.APPLICATION

    def test_create_cloud_resource_ci(self, test_db):
        """测试创建云资源类型配置项"""
        service = CIService(test_db)
        ci_in = CICreate(
            ci_type=CIType.CLOUD_RESOURCE,
            name="测试云主机",
            code="CLOUD-TEST-001",
            environment="production",
        )
        ci_details = {
            "cloud_provider": "aliyun",
            "resource_type": "ECS",
            "region": "cn-hangzhou",
            "cloud_resource_id": "i-xxxxx",
            "billing_type": "pay_as_you_go",
        }
        ci = service.create(ci_in, ci_details)
        assert ci.ci_type == CIType.CLOUD_RESOURCE
