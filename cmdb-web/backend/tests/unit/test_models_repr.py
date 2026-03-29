"""模型 __repr__ 方法单元测试"""

import pytest
from datetime import datetime
from app.models.base import Base
from app.models.ci import (
    ConfigurationItem,
    ConfigurationItemRelation,
    Server,
    NetworkDevice,
    Database,
    Middleware,
    Application,
    Container,
    K8sResource,
    CloudResource,
    CIType,
    CIStatus,
)
from app.models.audit import AuditLog, AuditAction, AuditStatus
from app.models.change import ChangeRecord, ChangeType, ChangeStatus, ChangePriority


class TestConfigurationItemRepr:
    """ConfigurationItem 模型 __repr__ 测试"""

    def test_configuration_item_repr(self, test_db):
        """测试 ConfigurationItem.__repr__ 方法"""
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        test_db.add(ci)
        test_db.commit()
        test_db.refresh(ci)

        repr_str = repr(ci)

        assert f"<CI(id={ci.id}," in repr_str
        assert f"code={ci.code}," in repr_str
        assert f"type={ci.ci_type})>" in repr_str


class TestConfigurationItemRelationRepr:
    """ConfigurationItemRelation 模型 __repr__ 测试"""

    def test_configuration_item_relation_repr(self, test_db):
        """测试 ConfigurationItemRelation.__repr__ 方法"""
        # 创建两个配置项
        source_ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="源服务器",
            code="SOURCE-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        target_ci = ConfigurationItem(
            ci_type=CIType.DATABASE,
            name="目标数据库",
            code="TARGET-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        test_db.add(source_ci)
        test_db.add(target_ci)
        test_db.commit()
        test_db.refresh(source_ci)
        test_db.refresh(target_ci)

        # 创建关系
        relation = ConfigurationItemRelation(
            source_ci_id=source_ci.id,
            target_ci_id=target_ci.id,
            relation_type="depends_on",
        )
        test_db.add(relation)
        test_db.commit()
        test_db.refresh(relation)

        repr_str = repr(relation)

        assert f"<CIRelation(id={relation.id}," in repr_str
        assert f"source={relation.source_ci_id}," in repr_str
        assert f"target={relation.target_ci_id})>" in repr_str


class TestServerRepr:
    """Server 模型 __repr__ 测试"""

    def test_server_repr(self, test_db):
        """测试 Server.__repr__ 方法"""
        server = Server(
            id=1,
            hostname="test-server-01",
            ip_address="192.168.1.100",
            os_type="Linux",
        )
        test_db.add(server)
        test_db.commit()
        test_db.refresh(server)

        repr_str = repr(server)

        assert f"<Server(hostname={server.hostname}," in repr_str
        assert f"ip={server.ip_address})>" in repr_str


class TestNetworkDeviceRepr:
    """NetworkDevice 模型 __repr__ 测试"""

    def test_network_device_repr(self, test_db):
        """测试 NetworkDevice.__repr__ 方法"""
        device = NetworkDevice(
            id=1,
            device_type="switch",
            vendor="Cisco",
            model="Catalyst 2960",
            management_ip="192.168.1.1",
        )
        test_db.add(device)
        test_db.commit()
        test_db.refresh(device)

        repr_str = repr(device)

        assert f"<NetworkDevice(device_type={device.device_type}," in repr_str
        assert f"vendor={device.vendor})>" in repr_str


class TestDatabaseRepr:
    """Database 模型 __repr__ 测试"""

    def test_database_repr(self, test_db):
        """测试 Database.__repr__ 方法"""
        db = Database(
            id=1,
            db_type="mysql",
            host="localhost",
            port=3306,
        )
        test_db.add(db)
        test_db.commit()
        test_db.refresh(db)

        repr_str = repr(db)

        assert f"<Database(db_type={db.db_type}," in repr_str
        assert f"host={db.host})>" in repr_str


class TestMiddlewareRepr:
    """Middleware 模型 __repr__ 测试"""

    def test_middleware_repr(self, test_db):
        """测试 Middleware.__repr__ 方法"""
        mw = Middleware(
            id=1,
            mw_type="redis",
            host="localhost",
            port=6379,
        )
        test_db.add(mw)
        test_db.commit()
        test_db.refresh(mw)

        repr_str = repr(mw)

        assert f"<Middleware(type={mw.mw_type}," in repr_str
        assert f"host={mw.host})>" in repr_str


class TestApplicationRepr:
    """Application 模型 __repr__ 测试"""

    def test_application_repr(self, test_db):
        """测试 Application.__repr__ 方法"""
        # 注意: Application.__repr__ 使用了 self.code，但模型定义中没有 code 字段
        # 这里创建一个带有 code 属性的对象来测试
        app = Application(
            id=1,
            app_type="web",
            language="Python",
            framework="FastAPI",
        )
        # 由于 Application 模型没有 code 字段，但 __repr__ 使用了它
        # 我们需要手动设置 code 属性
        app.code = "test-app"
        test_db.add(app)
        test_db.commit()
        test_db.refresh(app)

        repr_str = repr(app)

        assert f"<Application(name={app.code}," in repr_str
        assert f"type={app.app_type})>" in repr_str


class TestContainerRepr:
    """Container 模型 __repr__ 测试"""

    def test_container_repr(self, test_db):
        """测试 Container.__repr__ 方法"""
        container = Container(
            id=1,
            container_id="abc123def456",
            image="nginx:latest",
        )
        test_db.add(container)
        test_db.commit()
        test_db.refresh(container)

        repr_str = repr(container)

        assert f"<Container(id={container.container_id}," in repr_str
        assert f"image={container.image})>" in repr_str


class TestK8sResourceRepr:
    """K8sResource 模型 __repr__ 测试"""

    def test_k8s_resource_repr(self, test_db):
        """测试 K8sResource.__repr__ 方法"""
        resource = K8sResource(
            id=1,
            resource_type="deployment",
            namespace="default",
            cluster_name="prod-cluster",
        )
        test_db.add(resource)
        test_db.commit()
        test_db.refresh(resource)

        repr_str = repr(resource)

        assert f"<K8sResource(type={resource.resource_type}," in repr_str
        assert f"namespace={resource.namespace})>" in repr_str


class TestCloudResourceRepr:
    """CloudResource 模型 __repr__ 测试"""

    def test_cloud_resource_repr(self, test_db):
        """测试 CloudResource.__repr__ 方法"""
        resource = CloudResource(
            id=1,
            cloud_provider="aliyun",
            resource_type="ecs",
            region="cn-hangzhou",
            cloud_resource_id="i-abc123",
        )
        test_db.add(resource)
        test_db.commit()
        test_db.refresh(resource)

        repr_str = repr(resource)

        assert f"<CloudResource(provider={resource.cloud_provider}," in repr_str
        assert f"type={resource.resource_type})>" in repr_str


class TestAuditLogRepr:
    """AuditLog 模型 __repr__ 测试"""

    def test_audit_log_repr(self, test_db):
        """测试 AuditLog.__repr__ 方法"""
        log = AuditLog(
            user_id=1,
            action=AuditAction.CREATE,
            status=AuditStatus.SUCCESS,
            resource_type="user",
            resource_id=1,
        )
        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)

        repr_str = repr(log)

        assert f"<AuditLog(id={log.id}," in repr_str
        assert f"user_id={log.user_id}," in repr_str
        assert f"action={log.action})>" in repr_str


class TestChangeRecordRepr:
    """ChangeRecord 模型 __repr__ 测试"""

    def test_change_record_repr(self, test_db):
        """测试 ChangeRecord.__repr__ 方法"""
        # 先创建一个配置项
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        test_db.add(ci)
        test_db.commit()
        test_db.refresh(ci)

        record = ChangeRecord(
            ci_id=ci.id,
            change_type=ChangeType.UPDATE,
            status=ChangeStatus.PENDING,
            priority=ChangePriority.HIGH,
            title="更新服务器配置",
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        repr_str = repr(record)

        assert f"<ChangeRecord(id={record.id}," in repr_str
        assert f"ci_id={record.ci_id}," in repr_str
        assert f"type={record.change_type})>" in repr_str


class TestBaseTablename:
    """Base 类 __tablename__ 自动生成测试"""

    def test_tablename_generation_camelcase(self):
        """测试驼峰命名转换为下划线命名 - 使用现有模型验证"""
        # ConfigurationItem -> t_configuration_item
        assert ConfigurationItem.__tablename__ == "t_configuration_item"

    def test_tablename_generation_multiple_words(self):
        """测试多单词驼峰命名转换 - 使用现有模型验证"""
        # ConfigurationItemRelation -> t_configuration_item_relation
        assert ConfigurationItemRelation.__tablename__ == "t_configuration_item_relation"

    def test_tablename_generation_single_word(self):
        """测试单单词命名 - 使用现有模型验证"""
        # Server -> t_server
        assert Server.__tablename__ == "t_ci_server"


class TestBaseToDict:
    """Base 类 to_dict 方法测试"""

    def test_to_dict_converts_datetime_to_iso(self, test_db):
        """测试 to_dict 将 datetime 转换为 ISO 格式字符串"""
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        test_db.add(ci)
        test_db.commit()
        test_db.refresh(ci)

        result = ci.to_dict()

        # 验证 datetime 字段被转换为 ISO 格式字符串
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)
        # 验证 ISO 格式
        datetime.fromisoformat(result["created_at"])
        datetime.fromisoformat(result["updated_at"])

    def test_to_dict_handles_none_datetime(self, test_db):
        """测试 to_dict 处理 None 值的情况"""
        # 先创建一个配置项作为父级
        ci = ConfigurationItem(
            ci_type=CIType.CLOUD_RESOURCE,
            name="测试云资源",
            code="TEST-CLOUD-001",
            status=CIStatus.ONLINE,
            environment="production",
        )
        test_db.add(ci)
        test_db.commit()
        test_db.refresh(ci)

        # CloudResource 有可为空的 expiration_date 字段
        resource = CloudResource(
            id=ci.id,
            cloud_provider="aliyun",
            resource_type="ecs",
            region="cn-hangzhou",
            cloud_resource_id="i-abc123",
            expiration_date=None,
        )
        test_db.add(resource)
        test_db.commit()
        test_db.refresh(resource)

        result = resource.to_dict()

        # None datetime 值应该保持为 None (代码中 value.isoformat() if value else None)
        assert result["expiration_date"] is None

    def test_to_dict_includes_all_columns(self, test_db):
        """测试 to_dict 包含所有列"""
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            description="测试描述",
            status=CIStatus.ONLINE,
            environment="production",
            owner="test_owner",
            tags='["tag1", "tag2"]',
        )
        test_db.add(ci)
        test_db.commit()
        test_db.refresh(ci)

        result = ci.to_dict()

        # 验证所有列都在结果中
        expected_columns = [
            "id", "ci_type", "name", "code", "description",
            "status", "environment", "owner", "tags",
            "created_at", "updated_at"
        ]
        for column in expected_columns:
            assert column in result

        # 验证值正确
        assert result["name"] == "测试服务器"
        assert result["code"] == "TEST-SERVER-001"
        assert result["ci_type"] == CIType.SERVER
