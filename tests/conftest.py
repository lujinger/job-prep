import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User


# ── 测试数据库引擎 ──
SQLALCHEMY_TEST_URL = "sqlite:///./bookmark_test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── 覆盖依赖：测试时用测试库 ──
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── pytest fixture：TestClient ──
@pytest.fixture
def client():
    # 建表
    Base.metadata.create_all(bind=engine)

    # 只覆盖 get_db，不覆盖 get_current_user
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # 清理
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# ── pytest fixture：注册一个测试用户 ──
@pytest.fixture
def test_user(client):
    """确保测试库里有一个用户"""
    from app.dependencies import get_password_hash
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "username": "testuser", "password": "testpass123"}


# ── pytest fixture：获取 token ──
@pytest.fixture
def auth_headers(client, test_user):
    """登录获取 token，返回带 Authorization 头的 dict"""
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200, f"登录失败: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}