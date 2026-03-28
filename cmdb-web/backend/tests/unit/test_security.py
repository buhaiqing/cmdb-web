"""安全模块测试"""

import pytest
from app.core.security import hash_password, verify_password


class TestPasswordHashing:
    """密码哈希测试"""

    def test_hash_password_returns_string(self):
        """测试密码哈希返回字符串"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_hashes_for_same_password(self):
        """测试相同密码产生不同哈希（由于盐值）"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """测试验证正确密码"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_wrong_password(self):
        """测试验证错误密码"""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """测试验证空密码"""
        password = ""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_special_characters(self):
        """测试包含特殊字符的密码"""
        password = "P@$$w0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_unicode_characters(self):
        """测试包含 Unicode 字符的密码"""
        password = "密码 Password123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
