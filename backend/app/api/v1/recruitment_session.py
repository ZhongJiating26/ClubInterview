from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.recruitment_session import RecruitmentSession
from app.models.recruitment_session_position import RecruitmentSessionPosition
from app.models.club_position import ClubPosition
from app.repositories.club import ClubRepository
from app.repositories.recruitment_session import (
    RecruitmentSessionRepository,
    RecruitmentSessionPositionRepository,
)
from app.schemas.recruitment_session import (
    RecruitmentSessionCreate, RecruitmentSessionUpdate, RecruitmentSessionResponse,
    RecruitmentSessionPositionCreate, RecruitmentSessionPositionUpdate, RecruitmentSessionPositionResponse,
)


router = APIRouter(prefix="/recruitment/sessions", tags=["招新场次管理"])
session_repo = RecruitmentSessionRepository()
position_repo = RecruitmentSessionPositionRepository()
club_repo = ClubRepository()


def _load_positions(session: Session, sess: RecruitmentSession) -> RecruitmentSessionResponse:
    """加载场次关联的岗位"""
    positions = position_repo.get_by_session(session, sess.id)
    position_responses = []
    for p in positions:
        position_responses.append(RecruitmentSessionPositionResponse(
            id=p.id,
            session_id=p.session_id,
            position_id=p.position_id,
            position_name=p.position_name,
            position_description=p.position_description,
            position_requirement=p.position_requirement,
            recruit_quota=p.recruit_quota,
        ))
    return RecruitmentSessionResponse(
        id=sess.id,
        club_id=sess.club_id,
        name=sess.name,
        description=sess.description,
        start_time=sess.start_time,
        end_time=sess.end_time,
        max_candidates=sess.max_candidates,
        status=sess.status,
        created_by=sess.created_by,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        positions=position_responses,
    )


@router.get("", response_model=list[RecruitmentSessionResponse])
def list_sessions(
    club_id: Optional[int] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    获取招新场次列表
    """
    if club_id:
        # 检查社团是否存在
        club = club_repo.get(session, club_id)
        if not club or club.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社团不存在",
            )
        sessions = session_repo.get_by_club(session, club_id, status)
    else:
        sessions = session_repo.get_all(session)
        if status:
            sessions = [s for s in sessions if s.status == status]

    return [_load_positions(session, s) for s in sessions]


@router.post("", response_model=RecruitmentSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    club_id: int,
    data: RecruitmentSessionCreate,
    session: Session = Depends(get_session),
):
    """
    创建招新场次（社团管理员）
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 校验时间
    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始时间必须早于结束时间",
        )

    sess = RecruitmentSession(
        club_id=club_id,
        name=data.name,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        max_candidates=data.max_candidates,
        status=data.status,
    )

    try:
        session.add(sess)
        session.flush()

        seen_position_ids: set[int] = set()
        for item in data.positions:
            if item.position_id in seen_position_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="同一个岗位不能重复添加",
                )
            seen_position_ids.add(item.position_id)

            position = session.get(ClubPosition, item.position_id)
            if not position or position.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="岗位不存在",
                )

            pos = RecruitmentSessionPosition(
                session_id=sess.id,
                position_id=item.position_id,
                position_name=position.name,
                position_description=position.description,
                position_requirement=position.requirement,
                recruit_quota=item.recruit_quota,
            )
            session.add(pos)

        session.commit()
        session.refresh(sess)
    except HTTPException:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise

    return _load_positions(session, sess)


@router.get("/{session_id}", response_model=RecruitmentSessionResponse)
def get_recruitment_session(
    session_id: int,
    session: Session = Depends(get_session),
):
    """
    获取招新场次详情
    """
    sess = session_repo.get(session, session_id)
    if not sess or sess.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    return _load_positions(session, sess)


@router.put("/{session_id}", response_model=RecruitmentSessionResponse)
def update_session(
    session_id: int,
    data: RecruitmentSessionUpdate,
    session: Session = Depends(get_session),
):
    """
    更新招新场次（社团管理员）
    """
    sess = session_repo.get(session, session_id)
    if not sess or sess.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # 先校验时间（使用请求数据和当前数据库值的组合）
    new_start_time = data.start_time if data.start_time is not None else sess.start_time
    new_end_time = data.end_time if data.end_time is not None else sess.end_time

    if new_start_time >= new_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始时间必须早于结束时间",
        )

    # 更新字段
    if data.name is not None:
        sess.name = data.name
    if data.description is not None:
        sess.description = data.description
    if data.start_time is not None:
        sess.start_time = data.start_time
    if data.end_time is not None:
        sess.end_time = data.end_time
    if data.max_candidates is not None:
        sess.max_candidates = data.max_candidates
    if data.status is not None:
        sess.status = data.status

    sess.touch()
    session.commit()
    session.refresh(sess)

    return _load_positions(session, sess)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    session: Session = Depends(get_session),
):
    """
    删除招新场次（社团管理员）
    """
    sess = session_repo.get(session, session_id)
    if not sess or sess.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    session_repo.soft_delete(session, sess)
    session.commit()


@router.post("/{session_id}/positions", response_model=RecruitmentSessionPositionResponse, status_code=status.HTTP_201_CREATED)
def add_position(
    session_id: int,
    data: RecruitmentSessionPositionCreate,
    session: Session = Depends(get_session),
):
    """
    关联岗位到招新场次（社团管理员）
    """
    sess = session_repo.get(session, session_id)
    if not sess or sess.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # 检查岗位是否存在
    position = session.get(ClubPosition, data.position_id)
    if not position or position.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在",
        )

    # 检查是否已关联
    existing = position_repo.get_by_session_and_position(session, session_id, data.position_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该岗位已关联到此招新场次",
        )

    pos = RecruitmentSessionPosition(
        session_id=session_id,
        position_id=data.position_id,
        position_name=position.name,
        position_description=position.description,
        position_requirement=position.requirement,
        recruit_quota=data.recruit_quota,
    )
    session.add(pos)
    session.commit()
    session.refresh(pos)

    return RecruitmentSessionPositionResponse(
        id=pos.id,
        session_id=pos.session_id,
        position_id=pos.position_id,
        position_name=pos.position_name,
        position_description=pos.position_description,
        position_requirement=pos.position_requirement,
        recruit_quota=pos.recruit_quota,
    )


@router.put("/{session_id}/positions/{pos_id}", response_model=RecruitmentSessionPositionResponse)
def update_position(
    session_id: int,
    pos_id: int,
    data: RecruitmentSessionPositionUpdate,
    session: Session = Depends(get_session),
):
    """
    更新招新场次岗位的招聘配额（社团管理员）
    """
    pos = position_repo.get(session, pos_id)
    if not pos or pos.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联记录不存在",
        )
    if pos.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联记录不属于此招新场次",
        )

    # 更新配额
    if data.recruit_quota is not None:
        pos.recruit_quota = data.recruit_quota

    pos.touch()
    session.commit()
    session.refresh(pos)

    return RecruitmentSessionPositionResponse(
        id=pos.id,
        session_id=pos.session_id,
        position_id=pos.position_id,
        position_name=pos.position_name,
        position_description=pos.position_description,
        position_requirement=pos.position_requirement,
        recruit_quota=pos.recruit_quota,
    )


@router.delete("/{session_id}/positions/{pos_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_position(
    session_id: int,
    pos_id: int,
    session: Session = Depends(get_session),
):
    """
    取消关联岗位（社团管理员）
    """
    pos = position_repo.get(session, pos_id)
    if not pos or pos.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联记录不存在",
        )
    if pos.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联记录不属于此招新场次",
        )

    position_repo.soft_delete(session, pos)
    session.commit()


@router.get("/{session_id}/positions", response_model=list[RecruitmentSessionPositionResponse])
def list_session_positions(
    session_id: int,
    session: Session = Depends(get_session),
):
    """
    获取招新场次关联的岗位列表
    """
    sess = session_repo.get(session, session_id)
    if not sess or sess.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    positions = position_repo.get_by_session(session, session_id)
    return [
        RecruitmentSessionPositionResponse(
            id=p.id,
            session_id=p.session_id,
            position_id=p.position_id,
            position_name=p.position_name,
            position_description=p.position_description,
            position_requirement=p.position_requirement,
            recruit_quota=p.recruit_quota,
        )
        for p in positions
    ]
