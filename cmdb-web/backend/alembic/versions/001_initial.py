"""初始数据库迁移 - 创建所有表

Revision ID: initial
Revises:
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级迁移 - 创建所有表"""

    # ==================== 用户和权限表 ====================

    # 权限表
    op.create_table(
        't_permission',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_t_permission_code', 't_permission', ['code'], unique=False)
    op.create_index('ix_t_permission_resource', 't_permission', ['resource'], unique=False)

    # 角色表
    op.create_table(
        't_role',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_t_role_code', 't_role', ['code'], unique=False)

    # 用户表
    op.create_table(
        't_user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'locked', name='userstatus'), nullable=False, default='active'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index('ix_t_user_email', 't_user', ['email'], unique=False)
    op.create_index('ix_t_user_username', 't_user', ['username'], unique=False)

    # 用户 - 角色关联表
    op.create_table(
        't_user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['t_role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['t_user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
    )

    # 角色 - 权限关联表
    op.create_table(
        't_role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['t_permission.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['t_role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    # ==================== 配置项表 ====================

    # 配置项主表
    op.create_table(
        't_configuration_item',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ci_type', sa.Enum(
            'server', 'network_device', 'database', 'middleware',
            'application', 'container', 'k8s_resource', 'cloud_resource',
            name='citype'
        ), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('online', 'offline', 'maintenance', 'decommissioned', name='cistatus'), nullable=False, default='online'),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_t_configuration_item_ci_type', 't_configuration_item', ['ci_type'], unique=False)
    op.create_index('ix_t_configuration_item_code', 't_configuration_item', ['code'], unique=False)
    op.create_index('ix_t_configuration_item_environment', 't_configuration_item', ['environment'], unique=False)
    op.create_index('ix_t_configuration_item_name', 't_configuration_item', ['name'], unique=False)
    op.create_index('ix_t_configuration_item_status', 't_configuration_item', ['status'], unique=False)

    # 配置项关系表
    op.create_table(
        't_configuration_item_relation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_ci_id', sa.Integer(), nullable=False),
        sa.Column('target_ci_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_ci_id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_ci_id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_t_configuration_item_relation_relation_type', 't_configuration_item_relation', ['relation_type'], unique=False)
    op.create_index('ix_t_configuration_item_relation_source_ci_id', 't_configuration_item_relation', ['source_ci_id'], unique=False)
    op.create_index('ix_t_configuration_item_relation_target_ci_id', 't_configuration_item_relation', ['target_ci_id'], unique=False)

    # ==================== 具体 CI 类型表 ====================

    # 服务器表
    op.create_table(
        't_ci_server',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('os_type', sa.String(length=50), nullable=False),
        sa.Column('os_version', sa.String(length=50), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=True),
        sa.Column('memory_gb', sa.Integer(), nullable=True),
        sa.Column('disk_gb', sa.Integer(), nullable=True),
        sa.Column('cloud_provider', sa.String(length=50), nullable=True),
        sa.Column('instance_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 网络设备表
    op.create_table(
        't_ci_network_device',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=False),
        sa.Column('vendor', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('firmware_version', sa.String(length=50), nullable=True),
        sa.Column('management_ip', sa.String(length=45), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 数据库表
    op.create_table(
        't_ci_database',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('db_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('database_name', sa.String(length=100), nullable=True),
        sa.Column('master_ci_id', sa.Integer(), nullable=True),
        sa.Column('is_cluster', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_ci_id'], ['t_ci_database.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 中间件表
    op.create_table(
        't_ci_middleware',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mw_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 应用表
    op.create_table(
        't_ci_application',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_type', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('framework', sa.String(length=100), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('git_repo', sa.String(length=500), nullable=True),
        sa.Column('health_check_path', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 容器表
    op.create_table(
        't_ci_container',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('container_id', sa.String(length=64), nullable=False),
        sa.Column('image', sa.String(length=255), nullable=False),
        sa.Column('host_server_id', sa.Integer(), nullable=True),
        sa.Column('cpu_limit', sa.Float(), nullable=True),
        sa.Column('memory_limit_mb', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['host_server_id'], ['t_ci_server.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_t_ci_container_container_id', 't_ci_container', ['container_id'], unique=False)

    # K8s 资源表
    op.create_table(
        't_ci_k8s_resource',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('namespace', sa.String(length=100), nullable=False),
        sa.Column('cluster_name', sa.String(length=100), nullable=False),
        sa.Column('yaml_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 云资源表
    op.create_table(
        't_ci_cloud_resource',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cloud_provider', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=False),
        sa.Column('zone', sa.String(length=50), nullable=True),
        sa.Column('cloud_resource_id', sa.String(length=100), nullable=False),
        sa.Column('billing_type', sa.String(length=50), nullable=True),
        sa.Column('expiration_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_t_ci_cloud_resource_cloud_resource_id', 't_ci_cloud_resource', ['cloud_resource_id'], unique=False)

    # ==================== 变更管理表 ====================

    # 变更记录表
    op.create_table(
        't_change_record',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ci_id', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.Enum(
            'create', 'update', 'delete', 'relation_add', 'relation_remove',
            name='changetype'
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'pending', 'approved', 'rejected', 'in_progress', 'completed', 'rolled_back',
            name='changestatus'
        ), nullable=False, default='pending'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='changepriority'), nullable=False, default='medium'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ci_id'], ['t_configuration_item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['t_user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approver_id'], ['t_user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_t_change_record_ci_id', 't_change_record', ['ci_id'], unique=False)
    op.create_index('ix_t_change_record_change_type', 't_change_record', ['change_type'], unique=False)
    op.create_index('ix_t_change_record_status', 't_change_record', ['status'], unique=False)

    # ==================== 审计日志表 ====================

    # 审计日志表
    op.create_table(
        't_audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Enum(
            'login', 'logout', 'create', 'read', 'update', 'delete',
            'export', 'import', 'approve', 'reject', 'permission_change', 'role_change',
            name='auditaction'
        ), nullable=False),
        sa.Column('status', sa.Enum('success', 'failure', 'partial', name='auditstatus'), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=255), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['t_user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_t_audit_log_user_id', 't_audit_log', ['user_id'], unique=False)
    op.create_index('ix_t_audit_log_action', 't_audit_log', ['action'], unique=False)
    op.create_index('ix_t_audit_log_status', 't_audit_log', ['status'], unique=False)
    op.create_index('ix_t_audit_log_resource_type', 't_audit_log', ['resource_type'], unique=False)
    op.create_index('ix_t_audit_log_created_at', 't_audit_log', ['created_at'], unique=False)
    op.create_index('ix_t_audit_log_user_action', 't_audit_log', ['user_id', 'action'], unique=False)
    op.create_index('ix_t_audit_log_resource', 't_audit_log', ['resource_type', 'resource_id'], unique=False)

    # ==================== 插入初始数据 ====================

    # 插入默认角色
    op.bulk_insert(
        sa.table('t_role',
            sa.column('id', sa.Integer()),
            sa.column('name', sa.String()),
            sa.column('code', sa.String()),
            sa.column('description', sa.String()),
            sa.column('is_system', sa.Boolean()),
        ),
        [
            {'id': 1, 'name': '系统管理员', 'code': 'admin', 'description': '系统管理员，拥有所有权限', 'is_system': True},
            {'id': 2, 'name': '运维工程师', 'code': 'operator', 'description': '运维工程师，拥有配置项管理权限', 'is_system': True},
            {'id': 3, 'name': '只读用户', 'code': 'viewer', 'description': '只读用户，仅查看权限', 'is_system': True},
            {'id': 4, 'name': '审计员', 'code': 'auditor', 'description': '审计员，拥有审计日志查看权限', 'is_system': True},
        ]
    )

    # 插入默认权限
    op.bulk_insert(
        sa.table('t_permission',
            sa.column('id', sa.Integer()),
            sa.column('name', sa.String()),
            sa.column('code', sa.String()),
            sa.column('resource', sa.String()),
            sa.column('action', sa.String()),
        ),
        [
            {'id': 1, 'name': '查看配置项', 'code': 'ci:read', 'resource': 'ci', 'action': 'read'},
            {'id': 2, 'name': '创建配置项', 'code': 'ci:create', 'resource': 'ci', 'action': 'create'},
            {'id': 3, 'name': '编辑配置项', 'code': 'ci:update', 'resource': 'ci', 'action': 'update'},
            {'id': 4, 'name': '删除配置项', 'code': 'ci:delete', 'resource': 'ci', 'action': 'delete'},
            {'id': 5, 'name': '查看用户', 'code': 'user:read', 'resource': 'user', 'action': 'read'},
            {'id': 6, 'name': '创建用户', 'code': 'user:create', 'resource': 'user', 'action': 'create'},
            {'id': 7, 'name': '编辑用户', 'code': 'user:update', 'resource': 'user', 'action': 'update'},
            {'id': 8, 'name': '删除用户', 'code': 'user:delete', 'resource': 'user', 'action': 'delete'},
            {'id': 9, 'name': '查看审计日志', 'code': 'audit:read', 'resource': 'audit', 'action': 'read'},
            {'id': 10, 'name': '导出配置项', 'code': 'ci:export', 'resource': 'ci', 'action': 'export'},
        ]
    )

    # 分配角色权限
    # 系统管理员拥有所有权限
    op.bulk_insert(
        sa.table('t_role_permissions',
            sa.column('role_id', sa.Integer()),
            sa.column('permission_id', sa.Integer()),
        ),
        [
            {'role_id': 1, 'permission_id': pid} for pid in range(1, 11)
        ]
    )

    # 运维工程师拥有配置项所有权限和用户查看权限
    op.bulk_insert(
        sa.table('t_role_permissions',
            sa.column('role_id', sa.Integer()),
            sa.column('permission_id', sa.Integer()),
        ),
        [
            {'role_id': 2, 'permission_id': 1},  # ci:read
            {'role_id': 2, 'permission_id': 2},  # ci:create
            {'role_id': 2, 'permission_id': 3},  # ci:update
            {'role_id': 2, 'permission_id': 4},  # ci:delete
            {'role_id': 2, 'permission_id': 5},  # user:read
            {'role_id': 2, 'permission_id': 10}, # ci:export
        ]
    )

    # 只读用户仅有查看权限
    op.bulk_insert(
        sa.table('t_role_permissions',
            sa.column('role_id', sa.Integer()),
            sa.column('permission_id', sa.Integer()),
        ),
        [
            {'role_id': 3, 'permission_id': 1},  # ci:read
            {'role_id': 3, 'permission_id': 5},  # user:read
        ]
    )

    # 审计员有审计日志查看权限和配置项查看权限
    op.bulk_insert(
        sa.table('t_role_permissions',
            sa.column('role_id', sa.Integer()),
            sa.column('permission_id', sa.Integer()),
        ),
        [
            {'role_id': 4, 'permission_id': 1},  # ci:read
            {'role_id': 4, 'permission_id': 5},  # user:read
            {'role_id': 4, 'permission_id': 9},  # audit:read
        ]
    )


def downgrade() -> None:
    """回滚迁移 - 删除所有表"""
    op.drop_table('t_audit_log')
    op.drop_table('t_change_record')
    op.drop_table('t_ci_cloud_resource')
    op.drop_table('t_ci_k8s_resource')
    op.drop_table('t_ci_container')
    op.drop_table('t_ci_application')
    op.drop_table('t_ci_middleware')
    op.drop_table('t_ci_database')
    op.drop_table('t_ci_network_device')
    op.drop_table('t_ci_server')
    op.drop_table('t_configuration_item_relation')
    op.drop_table('t_configuration_item')
    op.drop_table('t_role_permissions')
    op.drop_table('t_user_roles')
    op.drop_table('t_user')
    op.drop_table('t_role')
    op.drop_table('t_permission')

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS auditstatus')
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS changepriority')
    op.execute('DROP TYPE IF EXISTS changestatus')
    op.execute('DROP TYPE IF EXISTS changetype')
    op.execute('DROP TYPE IF EXISTS cistatus')
    op.execute('DROP TYPE IF EXISTS citype')
    op.execute('DROP TYPE IF EXISTS userstatus')
