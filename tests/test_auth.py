import pytest


class TestRegister:
    def test_register_success(self, client):
        """注册成功"""
        response = client.post(
            "/register",
            json={"username": "newuser", "password": "newpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data

    def test_register_duplicate_username(self, client, test_user):
        """重复注册同一用户名 → 400"""
        response = client.post(
            "/register",
            json={"username": test_user["username"], "password": "whatever123"}
        )
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]


class TestLogin:
    def test_login_success(self, client, test_user):
        """登录成功 → 返回 token"""
        response = client.post(
            "/login",
            data={"username": test_user["username"], "password": test_user["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """密码错误 → 401"""
        response = client.post(
            "/login",
            data={"username": test_user["username"], "password": "wrongpass"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """不存在的用户 → 401"""
        response = client.post(
            "/login",
            data={"username": "nobody", "password": "nopass"}
        )
        assert response.status_code == 401