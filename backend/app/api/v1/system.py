from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user_account import UserAccount
from app.models.role import Role
from app.api.deps import get_current_user

router = APIRouter(prefix="/system", tags=["系统配置"])


# ==================== 系统角色 ====================

@router.get("/roles", response_model=List[dict])
async def get_system_roles(
    session: Session = Depends(get_session),
):
    """
    获取系统角色列表（无需登录）

    返回系统中所有可用的角色定义。
    """
    # 从数据库读取角色
    roles = session.exec(select(Role)).all()

    if roles:
        return [
            {
                "code": role.code.lower(),  # 转换为小写
                "name": role.name,
                "description": role.description or "",
                "sort_order": idx + 1
            }
            for idx, role in enumerate(roles)
        ]

    # 如果数据库没有，返回默认角色（小写 code）
    return [
        {"code": "student", "name": "普通学生", "description": "申请加入社团、参加面试", "sort_order": 1},
        {"code": "interviewer", "name": "面试官", "description": "参与面试评分、评审工作", "sort_order": 2},
        {"code": "admin", "name": "社团管理员", "description": "管理社团招新、面试安排等", "sort_order": 3},
    ]


# ==================== 社团分类 ====================

# 预设的社团分类（可以后续扩展为数据库表）
DEFAULT_CLUB_CATEGORIES = [
    {"id": "academic", "name": "学术科技类", "description": "学术、科技、研究类社团", "sort_order": 1},
    {"id": "culture", "name": "文化艺术类", "description": "文化、艺术、娱乐类社团", "sort_order": 2},
    {"id": "sports", "name": "体育健身类", "description": "体育、健身、运动类社团", "sort_order": 3},
    {"id": "public", "name": "公益服务类", "description": "公益、服务、志愿类社团", "sort_order": 4},
    {"id": "innovation", "name": "创新创业类", "description": "创新、创业、商业类社团", "sort_order": 5},
    {"id": "other", "name": "其他类", "description": "其他类型社团", "sort_order": 6},
]


@router.get("/club-categories", response_model=List[dict])
async def get_club_categories(
    session: Session = Depends(get_session),
):
    """
    获取社团分类列表（无需登录）

    返回系统中所有可用的社团分类。
    """
    # TODO: 后续可以从数据库表读取
    return DEFAULT_CLUB_CATEGORIES


# ==================== 学校列表 ====================

@router.get("/schools", response_model=List[dict])
async def get_schools(
    session: Session = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100, description="返回数量限制")
):
    """
    获取学校列表（无需登录）

    返回系统中的学校列表。
    """
    # 从数据库读取学校
    from app.models.school import School
    schools = session.exec(select(School).limit(limit)).all()

    if schools:
        return [
            {"code": school.code, "name": school.name}
            for school in schools
        ]

    # 如果数据库没有，返回空列表
    return []
