from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.department import Department
from app.repositories.club import ClubRepository
from app.repositories.department import DepartmentRepository
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
)


router = APIRouter(prefix="/clubs/{club_id}/departments", tags=["部门管理"])
dept_repo = DepartmentRepository()
club_repo = ClubRepository()


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    club_id: int,
    session: Session = Depends(get_session),
):
    """
    获取社团部门列表
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    return dept_repo.get_by_club(session, club_id)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    club_id: int,
    data: DepartmentCreate,
    session: Session = Depends(get_session),
):
    """
    创建部门（社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查同名部门是否存在
    existing = dept_repo.get_by_name(session, club_id, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该社团已存在同名部门",
        )

    dept = Department(
        club_id=club_id,
        name=data.name,
        description=data.description,
    )
    session.add(dept)
    session.commit()
    session.refresh(dept)

    return dept


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    club_id: int,
    dept_id: int,
    data: DepartmentUpdate,
    session: Session = Depends(get_session),
):
    """
    更新部门信息（社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查部门是否存在
    dept = dept_repo.get(session, dept_id)
    if not dept or dept.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在",
        )
    if dept.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门不属于该社团",
        )

    # 检查新名称是否与其他部门冲突
    if data.name and data.name != dept.name:
        existing = dept_repo.get_by_name(session, club_id, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该社团已存在同名部门",
            )

    # 更新字段
    if data.name is not None:
        dept.name = data.name
    if data.description is not None:
        dept.description = data.description

    dept.touch()
    session.commit()
    session.refresh(dept)

    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    club_id: int,
    dept_id: int,
    session: Session = Depends(get_session),
):
    """
    删除部门（逻辑删除，社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查部门是否存在
    dept = dept_repo.get(session, dept_id)
    if not dept or dept.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在",
        )
    if dept.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门不属于该社团",
        )

    dept_repo.soft_delete(session, dept)
    session.commit()
