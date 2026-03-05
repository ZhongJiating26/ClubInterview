import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.db.session import engine
from app.models.user_account import UserAccount
from app.repositories.user_account import UserAccountRepository

client = TestClient(app)
user_repo = UserAccountRepository()


@pytest.fixture
def db_session():
    with Session(engine) as session:
        yield session


@pytest.fixture
def uninitialized_user(db_session: Session) -> UserAccount:
    """
    创建一个“未初始化账号”（只有手机号、password_hash 为空）
    """
    phone = "13900000001"

    user = user_repo.get_by_phone(db_session, phone)
    if user:
        # 确保它是“未初始化”
        user.password_hash = None
        user.status = 1
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    user = UserAccount(
        phone=phone,
        password_hash=None,
        status=1,
        token_version=0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def login(phone: str, password: str):
    return client.post("/auth/login", json={"phone": phone, "password": password})


def test_auth_init_flow(db_session, uninitialized_user):
    # ---------- 1. 未登录直接 init（应该 401，因为路由存在但没认证） ----------
    resp = client.post("/auth/init", json={})
    assert resp.status_code == 401

    # ---------- 2. 为未初始化用户生成 token（模拟“注册后拿到 token”） ----------
    from app.core.security import create_access_token

    token = create_access_token(
        subject={
            "user_id": uninitialized_user.id,
            "token_version": uninitialized_user.token_version,
        }
    )
    headers = {"Authorization": f"Bearer {token}"}

    init_payload = {
        "password": "123456",
        "name": "测试用户",
        "id_card_no": "110101199001011234",
        "school_id": 1,
        "major": "计算机科学与技术",
        "student_no": "20230001",
        "email": "test@example.com",
    }

    # ---------- 3. 初始化账号（应成功） ----------
    resp = client.post("/auth/init", json=init_payload, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body

    # ---------- 4. 再次初始化（应 409） ----------
    resp = client.post("/auth/init", json=init_payload, headers=headers)
    assert resp.status_code == 409

    # ---------- 5. 初始化后可以正常登录 ----------
    resp = login(uninitialized_user.phone, "123456")
    assert resp.status_code == 200
    assert "access_token" in resp.json()
