from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile
from sqlmodel import Session, select, and_

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.club import Club
from app.models.role import Role
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.models.interview_session import InterviewSession
from app.models.interview_candidate import InterviewCandidate
from app.models.interview_record import InterviewRecord
from app.models.interview_session_interviewer import InterviewSessionInterviewer
from app.models.interview_session_score_item import InterviewSessionScoreItem
from app.models.score_item import ScoreItem
from app.models.score_template import ScoreTemplate
from app.models.signup_session import SignupSession
from app.models.interview_score import InterviewScore
from app.models.admission_result import AdmissionResult
from app.repositories.interview import (
    InterviewSessionRepository,
    InterviewCandidateRepository,
    InterviewRecordRepository,
    InterviewScoreRepository,
    AdmissionResultRepository,
)
from app.repositories.interview_session_interviewer import InterviewSessionInterviewerRepository
from app.repositories.interview_session_score_item import InterviewSessionScoreItemRepository
from app.repositories.score_template import ScoreTemplateRepository
from app.repositories.score_item import ScoreItemRepository as ScoreItemRepo
from app.schemas.interview import (
    InterviewSessionCreate, InterviewSessionUpdate, InterviewSessionResponse, InterviewSessionListResponse,
    InterviewCandidateCreate, InterviewCandidateResponse, InterviewCandidateDetailResponse,
    InterviewCandidateWithApplicationResponse,
    InterviewRecordCreate, InterviewRecordUpdate, InterviewRecordResponse,
    ScoreItemCreate, ScoreItemResponse,
    InterviewScoreCreate, InterviewScoreResponse,
    AdmissionResultUpdate, AdmissionResultResponse,
    InterviewSessionInterviewerCreate, InterviewSessionInterviewerResponse, SessionInterviewerResponse,
    InterviewSessionScoreItemCreate, InterviewSessionScoreItemResponse,
    SetScoreItemsRequest,
    AssignableInterviewerResponse,
    GenerateCandidatesRequest,
    ScoreTemplateResponse,
    ScoreItemDetailResponse,
    SetScoreTemplateRequest,
    SetScoreTemplateCustomItem,
)


router = APIRouter(prefix="/interview", tags=["面试管理"])
session_repo = InterviewSessionRepository()
session_interviewer_repo = InterviewSessionInterviewerRepository()
session_score_item_repo = InterviewSessionScoreItemRepository()
candidate_repo = InterviewCandidateRepository()
record_repo = InterviewRecordRepository()
score_repo = InterviewScoreRepository()
admission_repo = AdmissionResultRepository()
score_template_repo = ScoreTemplateRepository()
score_item_repo = ScoreItemRepo()


# ==================== 面试场次管理 ====================

@router.post("/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    club_id: int,
    data: InterviewSessionCreate,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """创建面试场次"""
    # 校验时间
    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始时间必须早于结束时间",
        )

    # 校验 status 值
    valid_statuses = ["DRAFT", "OPEN", "CLOSED"]
    if data.status and data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"状态值无效，必须是以下之一：{', '.join(valid_statuses)}",
        )

    session = InterviewSession(
        club_id=club_id,
        recruitment_session_id=data.recruitment_session_id,
        name=data.name,
        description=data.description,
        place=data.place,
        start_time=data.start_time,
        end_time=data.end_time,
        status=data.status or "DRAFT",
        created_by=current_user.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    return session


@router.get("/sessions", response_model=list[InterviewSessionListResponse])
def list_sessions(
    club_id: Optional[int] = None,
    recruitment_session_id: Optional[int] = None,
    status: Optional[str] = None,
    db_session: Session = Depends(get_session),
):
    """获取面试场次列表（包含统计字段）"""
    # 构建查询
    stmt = select(InterviewSession).where(InterviewSession.is_deleted == 0)

    if club_id:
        stmt = stmt.where(InterviewSession.club_id == club_id)
    if recruitment_session_id:
        stmt = stmt.where(InterviewSession.recruitment_session_id == recruitment_session_id)
    if status:
        stmt = stmt.where(InterviewSession.status == status)

    stmt = stmt.order_by(InterviewSession.created_at.desc())

    sessions = db_session.execute(stmt).scalars().all()

    # 为每个场次添加统计信息
    result = []
    for session in sessions:
        # 获取面试官数量
        interviewer_count = db_session.execute(
            select(InterviewSessionInterviewer)
            .where(InterviewSessionInterviewer.session_id == session.id)
            .where(InterviewSessionInterviewer.is_deleted == 0)
        ).scalars().all()
        interviewer_count = len(interviewer_count)

        # 获取候选人数
        candidate_count = db_session.execute(
            select(InterviewCandidate)
            .where(InterviewCandidate.session_id == session.id)
            .where(InterviewCandidate.is_deleted == 0)
        ).scalars().all()
        candidate_count = len(candidate_count)

        # 构建响应对象
        session_dict = {
            "id": session.id,
            "club_id": session.club_id,
            "recruitment_session_id": session.recruitment_session_id,
            "name": session.name,
            "description": session.description,
            "place": session.place,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "status": session.status,
            "created_by": session.created_by,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "interviewer_count": interviewer_count,
            "candidate_count": candidate_count,
        }
        result.append(session_dict)

    return result


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
def get_session_detail(
    session_id: int,
    db_session: Session = Depends(get_session),
):
    """获取面试场次详情"""
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )
    return session


@router.put("/sessions/{session_id}", response_model=InterviewSessionResponse)
def update_session(
    session_id: int,
    data: InterviewSessionUpdate,
    db_session: Session = Depends(get_session),
):
    """更新面试场次"""
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 更新字段
    if data.name is not None:
        session.name = data.name
    if data.description is not None:
        session.description = data.description
    if data.place is not None:
        session.place = data.place
    if data.start_time is not None:
        session.start_time = data.start_time
    if data.end_time is not None:
        session.end_time = data.end_time
    if data.status is not None:
        session.status = data.status

    # 校验时间
    if session.start_time >= session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始时间必须早于结束时间",
        )

    session.touch()
    db_session.commit()
    db_session.refresh(session)

    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db_session: Session = Depends(get_session),
):
    """
    删除面试场次（级联删除所有关联数据）

    级联删除：
    - 面试官分配记录
    - 候选人排期记录
    - 面试记录和评分
    - 该场次的评分项配置
    """
    interview_session = session_repo.get(db_session, session_id)
    if not interview_session or interview_session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 1. 删除面试官分配记录
    interviewer_relations = db_session.execute(
        select(InterviewSessionInterviewer)
        .where(InterviewSessionInterviewer.session_id == session_id)
        .where(InterviewSessionInterviewer.is_deleted == 0)
    ).scalars().all()
    for relation in interviewer_relations:
        session_interviewer_repo.soft_delete(db_session, relation)

    # 2. 获取候选人排期列表（用于删除面试记录）
    candidates = candidate_repo.get_by_session(db_session, session_id)

    # 3. 删除面试记录和评分
    for candidate in candidates:
        # 获取该候选人的面试记录
        records = db_session.execute(
            select(InterviewRecord)
            .where(InterviewRecord.candidate_id == candidate.id)
            .where(InterviewRecord.is_deleted == 0)
        ).scalars().all()
        for record in records:
            # 删除面试记录的评分
            scores = score_repo.get_by_record(db_session, record.id)
            for score in scores:
                score_repo.soft_delete(db_session, score)
            # 删除面试记录
            record_repo.soft_delete(db_session, record)
        # 删除候选人排期
        candidate_repo.soft_delete(db_session, candidate)

    # 4. 删除场次评分项配置
    score_item_relations = db_session.execute(
        select(InterviewSessionScoreItem)
        .where(InterviewSessionScoreItem.session_id == session_id)
        .where(InterviewSessionScoreItem.is_deleted == 0)
    ).scalars().all()
    for relation in score_item_relations:
        session_score_item_repo.soft_delete(db_session, relation)

    # 5. 删除面试场次
    session_repo.soft_delete(db_session, interview_session)
    db_session.commit()

    return None


# ==================== 候选人排期管理 ====================

@router.post("/sessions/{session_id}/generate-candidates", response_model=list[InterviewCandidateDetailResponse], status_code=status.HTTP_201_CREATED)
def generate_candidates(
    session_id: int,
    data: GenerateCandidatesRequest,
    db_session: Session = Depends(get_session),
):
    """生成候选人排期"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 确定开始时间和结束时间
    start_time = data.start_time or session.start_time
    end_time = data.end_time or session.end_time

    # 获取报名记录
    if data.signup_application_ids:
        # 使用指定的报名ID列表
        signup_sessions = db_session.execute(
            select(SignupSession)
            .where(SignupSession.id.in_(data.signup_application_ids))
            .where(SignupSession.is_deleted == 0)
        ).scalars().all()
    else:
        # 从该场次关联的招新场次中筛选已通过的报名
        signup_sessions = db_session.execute(
            select(SignupSession)
            .where(SignupSession.recruitment_session_id == session.recruitment_session_id)
            .where(SignupSession.status == "APPROVED")
            .where(SignupSession.is_deleted == 0)
        ).scalars().all()

    if not signup_sessions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有找到符合条件的报名记录",
        )

    # 生成候选人排期
    candidates = []
    current_time = start_time
    time_slot_duration = timedelta(minutes=data.time_slot_duration)

    for signup in signup_sessions:
        # 检查是否已存在候选人排期
        existing = db_session.execute(
            select(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.candidate_user_id == signup.user_id)
            .where(InterviewCandidate.is_deleted == 0)
        ).scalar_one_or_none()

        if existing:
            continue  # 跳过已存在的候选人

        # 计算计划开始和结束时间
        planned_start_time = current_time
        planned_end_time = current_time + time_slot_duration

        # 检查是否超出场次时间范围
        if planned_end_time > end_time:
            break

        # 创建候选人排期
        candidate = InterviewCandidate(
            session_id=session_id,
            signup_session_id=signup.id,
            candidate_user_id=signup.user_id,
            planned_start_time=planned_start_time,
            planned_end_time=planned_end_time,
            status="SCHEDULED",
        )
        db_session.add(candidate)
        db_session.commit()
        db_session.refresh(candidate)

        # 获取用户信息
        user = db_session.execute(
            select(UserAccount).where(UserAccount.id == signup.user_id)
        ).scalar_one_or_none()

        # 构建响应对象
        candidate_dict = {
            "id": candidate.id,
            "session_id": candidate.session_id,
            "signup_session_id": candidate.signup_session_id,
            "candidate_user_id": candidate.candidate_user_id,
            "user_name": user.name if user else None,
            "user_phone": user.phone if user else None,
            "position_id": None,  # 从 SignupSession 获取（如果需要）
            "position_name": None,
            "department_id": None,
            "department_name": None,
            "planned_start_time": candidate.planned_start_time,
            "planned_end_time": candidate.planned_end_time,
            "actual_start_time": candidate.actual_start_time,
            "actual_end_time": candidate.actual_end_time,
            "status": candidate.status,
            "final_score": candidate.final_score,
            "created_at": candidate.created_at,
        }
        candidates.append(candidate_dict)

        # 更新当前时间
        current_time = planned_end_time

    return candidates


@router.get("/sessions/{session_id}/candidates", response_model=list[InterviewCandidateDetailResponse])
def list_candidates(
    session_id: int,
    status: Optional[str] = None,
    db_session: Session = Depends(get_session),
):
    """获取场次的候选人列表（支持状态筛选）"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 构建查询
    stmt = (
        select(InterviewCandidate)
        .where(InterviewCandidate.session_id == session_id)
        .where(InterviewCandidate.is_deleted == 0)
    )
    if status:
        stmt = stmt.where(InterviewCandidate.status == status)

    stmt = stmt.order_by(InterviewCandidate.planned_start_time)

    candidates = db_session.execute(stmt).scalars().all()

    # 构建响应对象
    result = []
    for candidate in candidates:
        # 获取用户信息
        user = db_session.execute(
            select(UserAccount).where(UserAccount.id == candidate.candidate_user_id)
        ).scalar_one_or_none()

        candidate_dict = {
            "id": candidate.id,
            "session_id": candidate.session_id,
            "signup_session_id": candidate.signup_session_id,
            "candidate_user_id": candidate.candidate_user_id,
            "user_name": user.name if user else None,
            "user_phone": user.phone if user else None,
            "position_id": None,
            "position_name": None,
            "department_id": None,
            "department_name": None,
            "planned_start_time": candidate.planned_start_time,
            "planned_end_time": candidate.planned_end_time,
            "actual_start_time": candidate.actual_start_time,
            "actual_end_time": candidate.actual_end_time,
            "status": candidate.status,
            "final_score": candidate.final_score,
            "created_at": candidate.created_at,
        }
        result.append(candidate_dict)

    return result


@router.get("/candidates/{candidate_id}", response_model=InterviewCandidateWithApplicationResponse)
def get_candidate(
    candidate_id: int,
    db_session: Session = Depends(get_session),
):
    """获取候选人详情（包含报名信息）"""
    candidate = candidate_repo.get(db_session, candidate_id)
    if not candidate or candidate.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人排期不存在",
        )

    # 获取用户信息
    user = db_session.execute(
        select(UserAccount).where(UserAccount.id == candidate.candidate_user_id)
    ).scalar_one_or_none()

    # 获取报名信息
    application = None
    if candidate.signup_session_id:
        signup = db_session.execute(
            select(SignupSession).where(SignupSession.id == candidate.signup_session_id)
        ).scalar_one_or_none()
        if signup:
            application = {
                "id": signup.id,
                "user_id": signup.user_id,
                "recruitment_session_id": signup.recruitment_session_id,
                "status": signup.status,
                "self_intro": signup.self_intro,
            }

    return {
        "id": candidate.id,
        "session_id": candidate.session_id,
        "signup_session_id": candidate.signup_session_id,
        "candidate_user_id": candidate.candidate_user_id,
        "user_name": user.name if user else None,
        "user_phone": user.phone if user else None,
        "position_id": None,
        "position_name": None,
        "department_id": None,
        "department_name": None,
        "planned_start_time": candidate.planned_start_time,
        "planned_end_time": candidate.planned_end_time,
        "actual_start_time": candidate.actual_start_time,
        "actual_end_time": candidate.actual_end_time,
        "status": candidate.status,
        "final_score": candidate.final_score,
        "created_at": candidate.created_at,
        "application": application,
    }


# ==================== 面试记录管理 ====================

@router.put("/records/{record_id}", response_model=InterviewRecordResponse)
def update_record(
    record_id: int,
    data: InterviewRecordUpdate,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    更新面试记录（不含评分）

    支持更新：
    - summary: 总结
    - record_text: 手写记录
    - recording_url: 录音URL
    - face_image_url: 照片URL
    """
    record = record_repo.get(db_session, record_id)
    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在",
        )

    # 验证是否为记录的创建者
    if record.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限修改此面试记录",
        )

    if data.summary is not None:
        record.summary = data.summary
    if data.record_text is not None:
        record.record_text = data.record_text
    if data.recording_url is not None:
        record.recording_url = data.recording_url
    if data.face_image_url is not None:
        record.face_image_url = data.face_image_url

    record.touch()
    db_session.commit()
    db_session.refresh(record)

    return record


@router.get("/my-tasks", response_model=list[InterviewCandidateDetailResponse])
def get_my_tasks(
    club_id: Optional[int] = None,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    获取面试官的任务列表

    返回当前登录面试官需要面试的候选人列表
    支持按社团筛选
    """
    # 获取该面试官关联的所有场次
    stmt = (
        select(InterviewSessionInterviewer)
        .where(InterviewSessionInterviewer.interviewer_id == current_user.id)
        .where(InterviewSessionInterviewer.is_deleted == 0)
    )
    if club_id:
        # 获取该社团的场次
        session_stmt = (
            select(InterviewSession)
            .where(InterviewSession.club_id == club_id)
            .where(InterviewSession.is_deleted == 0)
        )
        sessions = db_session.execute(session_stmt).scalars().all()
        session_ids = [s.id for s in sessions]
        stmt = stmt.where(InterviewSessionInterviewer.session_id.in_(session_ids))

    interviewer_assignments = db_session.execute(stmt).scalars().all()
    session_ids = [ia.session_id for ia in interviewer_assignments]

    if not session_ids:
        return []

    # 获取这些场次的所有候选人
    stmt = (
        select(InterviewCandidate)
        .where(InterviewCandidate.session_id.in_(session_ids))
        .where(InterviewCandidate.is_deleted == 0)
        .order_by(InterviewCandidate.planned_start_time)
    )
    candidates = db_session.execute(stmt).scalars().all()

    # 构建响应列表
    results = []
    for candidate in candidates:
        # 获取用户信息
        user = db_session.execute(
            select(UserAccount).where(UserAccount.id == candidate.candidate_user_id)
        ).scalar_one_or_none()

        # 获取报名信息
        signup_session = None
        if candidate.signup_session_id:
            signup_session = db_session.execute(
                select(SignupSession).where(SignupSession.id == candidate.signup_session_id)
            ).scalar_one_or_none()

        results.append({
            "id": candidate.id,
            "session_id": candidate.session_id,
            "signup_session_id": candidate.signup_session_id,
            "candidate_user_id": candidate.candidate_user_id,
            "user_name": user.name if user else None,
            "user_phone": user.phone if user else None,
            "position_id": signup_session.position_id if signup_session else None,
            "position_name": None,  # 需要关联查询
            "department_id": signup_session.department_id if signup_session else None,
            "department_name": None,  # 需要关联查询
            "planned_start_time": candidate.planned_start_time,
            "planned_end_time": candidate.planned_end_time,
            "actual_start_time": candidate.actual_start_time,
            "actual_end_time": candidate.actual_end_time,
            "status": candidate.status,
            "final_score": candidate.final_score,
            "created_at": candidate.created_at,
        })

    return results


# ==================== 评分管理 ====================

@router.post("/records/{record_id}/scores", response_model=InterviewScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(
    record_id: int,
    data: InterviewScoreCreate,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    为面试记录添加评分

    创建单项评分，不会自动计算总分
    """
    record = record_repo.get(db_session, record_id)
    if not record or record.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在",
        )

    # 验证是否为记录的创建者
    if record.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限为此记录添加评分",
        )

    # 获取评分项信息
    score_item = score_item_repo.get(db_session, data.score_item_id)
    if not score_item or score_item.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评分项不存在",
        )

    # 检查是否已经为该记录添加过此评分项
    existing_score = db_session.execute(
        select(InterviewScore)
        .where(InterviewScore.record_id == record_id)
        .where(InterviewScore.score_item_id == data.score_item_id)
        .where(InterviewScore.is_deleted == 0)
    ).scalar_one_or_none()
    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已存在该评分项的评分，请使用更新接口修改",
        )

    # 校验分数
    if data.score > score_item.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分数不能超过满分 {score_item.max_score}",
        )

    interview_score = InterviewScore(
        record_id=record_id,
        score_item_id=data.score_item_id,
        item_name=score_item.name,
        item_weight=score_item.weight,
        item_max_score=score_item.max_score,
        score=data.score,
        remark=data.remark,
    )
    db_session.add(interview_score)
    db_session.commit()
    db_session.refresh(interview_score)

    return interview_score


@router.get("/records/{record_id}/scores", response_model=list[InterviewScoreResponse])
def list_scores(
    record_id: int,
    db_session: Session = Depends(get_session),
):
    """获取面试记录的评分列表"""
    return score_repo.get_by_record(db_session, record_id)


# ==================== 录取结果管理 ====================

@router.put("/candidates/{candidate_id}/admission", response_model=AdmissionResultResponse)
def update_admission(
    candidate_id: int,
    data: AdmissionResultUpdate,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    设置候选人录取结果

    该接口会：
    1. 验证权限
    2. 创建或更新录取结果
    3. 记录决策人和决策时间
    """
    candidate = candidate_repo.get(db_session, candidate_id)
    if not candidate or candidate.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人排期不存在",
        )

    # 获取场次信息，验证权限
    session = session_repo.get(db_session, candidate.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 验证用户是否为该社团的管理员
    stmt = (
        select(Role)
        .where(Role.code == "CLUB_ADMIN")
        .where(Role.is_deleted == 0)
    )
    admin_role = db_session.execute(stmt).scalar_one_or_none()
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.role_id == admin_role.id)
        .where(UserRole.club_id == session.club_id)
        .where(UserRole.is_deleted == 0)
    )
    user_role = db_session.execute(stmt).scalar_one_or_none()
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该社团的管理员，无权设置录取结果",
        )

    # 查找或创建录取结果
    admission = admission_repo.get_by_candidate(db_session, candidate.candidate_user_id)
    if not admission:
        admission = AdmissionResult(
            interview_candidate_id=candidate_id,
            candidate_user_id=candidate.candidate_user_id,
            final_score_snapshot=candidate.final_score,
        )
        db_session.add(admission)
        db_session.flush()

    # 更新录取结果
    admission.result = data.result
    admission.department_id = data.department_id
    admission.position_id = data.position_id
    admission.remark = data.remark
    admission.decided_by = current_user.id
    admission.decided_at = datetime.now()
    admission.touch()

    db_session.commit()
    db_session.refresh(admission)

    return admission


@router.get("/sessions/{session_id}/results-summary")
def get_session_results_summary(
    session_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    获取场次面试结果汇总

    返回该场次所有候选人的面试结果，包括：
    - 候选人基本信息
    - 面试记录列表
    - 各面试官的评分
    - 平均分
    - 录取结果
    """
    # 验证场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 验证用户是否为该社团的成员
    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.club_id == session.club_id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = db_session.execute(stmt).scalars().all()
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该社团的成员",
        )

    # 获取该场次的所有候选人
    stmt = (
        select(InterviewCandidate)
        .where(InterviewCandidate.session_id == session_id)
        .where(InterviewCandidate.is_deleted == 0)
        .order_by(InterviewCandidate.final_score.desc())
    )
    candidates = db_session.execute(stmt).scalars().all()

    # 构建结果列表
    results = []
    for candidate in candidates:
        # 获取用户信息
        user = db_session.execute(
            select(UserAccount).where(UserAccount.id == candidate.candidate_user_id)
        ).scalar_one_or_none()

        # 获取该候选人的所有面试记录
        stmt = (
            select(InterviewRecord)
            .where(InterviewRecord.session_id == session_id)
            .where(InterviewRecord.candidate_user_id == candidate.candidate_user_id)
            .where(InterviewRecord.is_deleted == 0)
        )
        records = db_session.execute(stmt).scalars().all()

        # 获取录取结果
        admission = admission_repo.get_by_candidate(db_session, candidate.candidate_user_id)

        # 构建记录详情
        records_detail = []
        for record in records:
            # 获取面试官信息
            interviewer = db_session.execute(
                select(UserAccount).where(UserAccount.id == record.interviewer_id)
            ).scalar_one_or_none()

            # 获取评分明细
            scores = score_repo.get_by_record(db_session, record.id)

            records_detail.append({
                "record_id": record.id,
                "interviewer_name": interviewer.name if interviewer else "未知",
                "status": record.status,
                "total_score": record.total_score,
                "summary": record.summary,
                "scores": [
                    {
                        "item_name": s.item_name,
                        "score": s.score,
                        "max_score": s.item_max_score,
                        "weight": s.item_weight,
                    }
                    for s in scores
                ],
            })

        results.append({
            "candidate_id": candidate.id,
            "user_id": candidate.candidate_user_id,
            "user_name": user.name if user else "未知",
            "user_phone": user.phone if user else None,
            "status": candidate.status,
            "final_score": candidate.final_score,
            "admission_result": admission.result if admission else None,
            "admission_department_id": admission.department_id if admission else None,
            "admission_position_id": admission.position_id if admission else None,
            "records": records_detail,
            "interviewer_count": len(records),
        })

    return {
        "session_id": session_id,
        "session_name": session.name,
        "candidate_count": len(candidates),
        "results": results,
    }


# ==================== 面试官管理 ====================

@router.post("/sessions/{session_id}/interviewers", response_model=InterviewSessionInterviewerResponse, status_code=status.HTTP_201_CREATED)
def add_interviewer_to_session(
    session_id: int,
    data: InterviewSessionInterviewerCreate,
    db_session: Session = Depends(get_session),
):
    """添加面试官到场次"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 根据 user_role 表的 id 获取用户 id
    user_role = db_session.execute(
        select(UserRole).where(UserRole.id == data.interviewer_id).where(UserRole.is_deleted == 0)
    ).scalar_one_or_none()

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试官记录不存在",
        )

    # 检查是否已分配
    existing = db_session.execute(
        select(InterviewSessionInterviewer)
        .where(InterviewSessionInterviewer.session_id == session_id)
        .where(InterviewSessionInterviewer.interviewer_id == user_role.user_id)
        .where(InterviewSessionInterviewer.is_deleted == 0)
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该面试官已分配到此场次",
        )

    # 添加面试官到场次
    relation = InterviewSessionInterviewer(
        session_id=session_id,
        interviewer_id=user_role.user_id,
        role="INTERVIEWER",
    )
    db_session.add(relation)
    db_session.commit()
    db_session.refresh(relation)

    return relation


@router.get("/sessions/{session_id}/interviewers", response_model=list[SessionInterviewerResponse])
def get_session_interviewers(
    session_id: int,
    db_session: Session = Depends(get_session),
):
    """获取场次的所有面试官（包含用户信息）"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 获取场次的面试官关联
    interviewer_relations = session_interviewer_repo.get_by_session(db_session, session_id)

    # 获取用户详细信息
    result = []
    for relation in interviewer_relations:
        user = db_session.execute(
            select(UserAccount).where(UserAccount.id == relation.interviewer_id)
        ).scalar_one_or_none()

        if user:
            # 获取用户在该社团的 club_id
            user_role = db_session.execute(
                select(UserRole)
                .where(UserRole.user_id == user.id)
                .where(UserRole.club_id == session.club_id)
                .where(UserRole.is_deleted == 0)
            ).first()

            club_id = user_role[0].club_id if user_role else session.club_id

            result.append({
                "id": relation.id,
                "user_id": user.id,
                "club_id": club_id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
            })

    return result


# ==================== 评分项管理 ====================

@router.post("/sessions/{session_id}/score-items", response_model=InterviewSessionScoreItemResponse, status_code=status.HTTP_201_CREATED)
def add_score_item_to_session(
    session_id: int,
    data: InterviewSessionScoreItemCreate,
    db_session: Session = Depends(get_session),
):
    """添加评分项到场次"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    relation = session_score_item_repo.add_score_item(
        db_session,
        session_id,
        data.score_item_id,
        data.order_no,
    )

    return relation


@router.get("/sessions/{session_id}/score-items", response_model=list[InterviewSessionScoreItemResponse])
def get_session_score_items(
    session_id: int,
    db_session: Session = Depends(get_session),
):
    """获取场次的所有评分项（按顺序）"""
    # 检查场次是否存在
    session = session_repo.get(db_session, session_id)
    if not session or session.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    return session_score_item_repo.get_by_session(db_session, session_id)


# ==================== 可分配面试官管理 ====================

@router.get("/clubs/{club_id}/assignable-interviewers", response_model=list[AssignableInterviewerResponse])
def get_assignable_interviewers(
    club_id: int,
    db_session: Session = Depends(get_session),
):
    """
    获取社团可分配的面试官列表

    返回该社团的所有 CLUB_ADMIN 和 INTERVIEWER 角色的用户
    - 如果用户既是 CLUB_ADMIN 又是 INTERVIEWER，只保留 CLUB_ADMIN 角色
    - 排序：CLUB_ADMIN 在前，同角色按姓名字母顺序排列
    """
    # 检查社团是否存在
    club = db_session.execute(
        select(Club).where(Club.id == club_id).where(Club.is_deleted == 0)
    ).scalar_one_or_none()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 获取 CLUB_ADMIN 和 INTERVIEWER 角色
    admin_role = db_session.execute(
        select(Role).where(Role.code == "CLUB_ADMIN").where(Role.is_deleted == 0)
    ).scalar_one_or_none()
    interviewer_role = db_session.execute(
        select(Role).where(Role.code == "INTERVIEWER").where(Role.is_deleted == 0)
    ).scalar_one_or_none()

    if not admin_role or not interviewer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    # 查询该社团的 CLUB_ADMIN 用户
    admin_users = []
    if admin_role:
        admin_stmt = (
            select(UserRole, UserAccount)
            .join(UserAccount, UserRole.user_id == UserAccount.id)
            .where(UserRole.role_id == admin_role.id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
            .where(UserAccount.status == 1)
        )
        admin_results = db_session.execute(admin_stmt).all()
        for user_role, user in admin_results:
            admin_users.append({
                "id": user_role.id,
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "role": "CLUB_ADMIN",
            })

    # 查询该社团的 INTERVIEWER 用户
    interviewer_users = []
    if interviewer_role:
        interviewer_stmt = (
            select(UserRole, UserAccount)
            .join(UserAccount, UserRole.user_id == UserAccount.id)
            .where(UserRole.role_id == interviewer_role.id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
            .where(UserAccount.status == 1)
        )
        interviewer_results = db_session.execute(interviewer_stmt).all()
        for user_role, user in interviewer_results:
            interviewer_users.append({
                "id": user_role.id,
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "role": "INTERVIEWER",
            })

    # 合并列表，去重（优先保留 CLUB_ADMIN）
    user_dict = {}
    for user in admin_users:
        user_dict[user["user_id"]] = user

    for user in interviewer_users:
        if user["user_id"] not in user_dict:
            user_dict[user["user_id"]] = user

    # 转换为列表并排序
    result_list = list(user_dict.values())
    result_list.sort(key=lambda x: (0 if x["role"] == "CLUB_ADMIN" else 1, x["name"] or ""))

    return result_list


# ==================== 评分模板管理 ====================

@router.get("/score-templates", response_model=list[ScoreTemplateResponse])
def get_score_templates(
    club_id: int,
    status: Optional[str] = None,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    获取评分模板列表

    Args:
        club_id: 社团ID
        status: 状态筛选（ACTIVE/INACTIVE），不传则返回所有状态

    Returns:
        评分模板列表
    """
    # 验证用户是否有权限查看该社团的模板
    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.club_id == club_id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = db_session.execute(stmt).scalars().all()
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该社团的成员",
        )

    # 如果传入状态参数，验证状态值
    if status and status not in ["ACTIVE", "INACTIVE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态值无效，必须是 ACTIVE 或 INACTIVE",
        )

    templates = score_template_repo.get_by_club(db_session, club_id, status=status)

    # 标记默认模板（第一个创建的模板）
    result = []
    for i, template in enumerate(templates):
        template_dict = {
            "id": template.id,
            "club_id": template.club_id,
            "name": template.name,
            "description": template.description,
            "is_default": (i == len(templates) - 1),  # 最后一个是默认模板（最早创建）
            "created_at": template.created_at,
            "updated_at": template.updated_at,
        }
        result.append(template_dict)

    # 按创建时间倒序排列（默认模板在最后）
    result.reverse()
    return result


@router.get("/score-templates/{template_id}/items", response_model=list[ScoreItemDetailResponse])
def get_template_score_items(
    template_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    获取模板的评分项列表

    Args:
        template_id: 模板ID

    Returns:
        评分项列表（按sort_order排序）
    """
    # 获取模板
    template = score_template_repo.get(db_session, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评分模板不存在",
        )

    # 验证用户是否有权限查看该社团的模板
    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.club_id == template.club_id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = db_session.execute(stmt).scalars().all()
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此模板的评分项",
        )

    # 获取评分项
    items = score_item_repo.get_by_template(db_session, template_id)

    # 转换为响应格式
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "template_id": item.template_id,
            "session_id": item.session_id,
            "title": item.name,
            "description": None,
            "max_score": item.max_score,
            "weight": item.weight,
            "sort_order": item.order_no,
        })

    return result


@router.post("/sessions/{session_id}/score-template")
def set_session_score_template(
    session_id: int,
    data: SetScoreTemplateRequest,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """
    设置场次的评分模板或自定义评分项

    Args:
        session_id: 面试场次ID
        data: 请求数据，包含template_id或custom_items

    Returns:
        设置结果
    """
    # 获取场次
    session = session_repo.get(db_session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试场次不存在",
        )

    # 验证用户是否有权限操作该社团的场次
    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.club_id == session.club_id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = db_session.execute(stmt).scalars().all()
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限操作此场次",
        )

    # 删除场次现有的评分项关联
    existing_items = session_score_item_repo.get_by_session(db_session, session_id)
    for item in existing_items:
        session_score_item_repo.soft_delete(db_session, item)

    # 删除场次的自定义评分项
    score_item_repo.delete_by_session(db_session, session_id)

    if data.template_id:
        # 使用已有模板
        template = score_template_repo.get(db_session, data.template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评分模板不存在",
            )

        if template.club_id != session.club_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板不属于该社团",
            )

        # 复制模板的评分项到场次
        template_items = score_item_repo.get_by_template(db_session, data.template_id)
        for item in template_items:
            # 创建关联记录
            session_score_item = InterviewSessionScoreItem(
                session_id=session_id,
                score_item_id=item.id,
                order_no=item.order_no,
            )
            db_session.add(session_score_item)

    elif data.custom_items:
        # 使用自定义评分项
        for order_no, item_data in enumerate(data.custom_items, start=1):
            custom_item = ScoreItem(
                template_id=None,
                session_id=session_id,
                name=item_data.title,
                description=item_data.description,
                max_score=item_data.max_score,
                weight=item_data.weight,
                order_no=order_no,
            )
            db_session.add(custom_item)
            db_session.flush()

            # 创建关联记录
            session_score_item = InterviewSessionScoreItem(
                session_id=session_id,
                score_item_id=custom_item.id,
                order_no=order_no,
            )
            db_session.add(session_score_item)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须指定template_id或custom_items",
        )

    db_session.commit()

    return {
        "message": "评分模板设置成功",
        "session_id": session_id,
    }


