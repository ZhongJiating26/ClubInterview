from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.club_position import ClubPosition
from app.repositories.club import ClubRepository
from app.repositories.club_position import ClubPositionRepository
from app.schemas.club_position import (
    PositionCreate, PositionUpdate, PositionResponse,
)


router = APIRouter(prefix="/clubs/{club_id}/positions", tags=["岗位管理"])
position_repo = ClubPositionRepository()
club_repo = ClubRepository()


@router.get("", response_model=list[PositionResponse])
def list_positions(
    club_id: int,
    department_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """
    获取社团岗位列表
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    return position_repo.get_by_club(session, club_id, department_id)


@router.post("", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(
    club_id: int,
    data: PositionCreate,
    session: Session = Depends(get_session),
):
    """
    创建岗位（社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查同名岗位是否存在
    existing = position_repo.get_by_name(session, club_id, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该社团已存在同名岗位",
        )

    position = ClubPosition(
        club_id=club_id,
        department_id=data.department_id,
        name=data.name,
        description=data.description,
        requirement=data.requirement,
    )
    session.add(position)
    session.commit()
    session.refresh(position)

    return position


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(
    club_id: int,
    position_id: int,
    data: PositionUpdate,
    session: Session = Depends(get_session),
):
    """
    更新岗位信息（社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查岗位是否存在
    position = position_repo.get(session, position_id)
    if not position or position.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在",
        )
    if position.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="岗位不属于该社团",
        )

    # 检查新名称是否与其他岗位冲突
    if data.name and data.name != position.name:
        existing = position_repo.get_by_name(session, club_id, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该社团已存在同名岗位",
            )

    # 更新字段
    if data.department_id is not None:
        position.department_id = data.department_id
    if data.name is not None:
        position.name = data.name
    if data.description is not None:
        position.description = data.description
    if data.requirement is not None:
        position.requirement = data.requirement

    position.touch()
    session.commit()
    session.refresh(position)

    return position


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position(
    club_id: int,
    position_id: int,
    session: Session = Depends(get_session),
):
    """
    删除岗位（逻辑删除，社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查岗位是否存在
    position = position_repo.get(session, position_id)
    if not position or position.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在",
        )
    if position.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="岗位不属于该社团",
        )

    position_repo.soft_delete(session, position)
    session.commit()
