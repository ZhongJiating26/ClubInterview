from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.api.deps import get_current_user
from app.models.user_account import UserAccount
from app.models.signup_session import SignupSession
from app.models.signup_item import SignupItem
from app.models.interview_candidate import InterviewCandidate
from app.models.interview_record import InterviewRecord
from app.models.interview_session import InterviewSession
from app.models.admission_result import AdmissionResult
from app.models.recruitment_session import RecruitmentSession
from app.models.club_position import ClubPosition
from app.models.department import Department
from app.models.ticket import Ticket, TicketReply
from app.models.notification import Notification
from app.models.notification_user import NotificationUser

from app.schemas.student import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    InterviewResponse, InterviewConfirmationUpdate, InterviewResultResponse,
    NotificationResponse, NotificationUnreadCountResponse,
    TicketCreate, TicketMessageCreate, TicketResponse, TicketReplyResponse,
    StudentProfileResponse, StudentProfileUpdate, ApplicationStatsResponse,
    ProfileResponse, ProfileData,
    FAQResponse,
    SignupSubmitResponse, SignupApplicationListResponse, SignupApplicationData, SignupItemData,
    SignupApplicationDetailData,
    StudentInterviewRecordData, StudentInterviewRecordDetailData,
    InterviewSessionInfoData, SignupApplicationInfoData,
)

from app.repositories.signup_session import SignupSessionRepository, SignupItemRepository
from app.repositories.interview import (
    InterviewCandidateRepository,
    InterviewRecordRepository,
    AdmissionResultRepository,
)
from app.repositories.student import (
    NotificationRepository,
    TicketRepository,
    TicketReplyRepository,
    FAQRepository,
)
from app.repositories.user_account import UserAccountRepository
from app.repositories.club_position import ClubPositionRepository


router = APIRouter(prefix="/student", tags=["学生端"])

# Repositories
signup_session_repo = SignupSessionRepository()
signup_item_repo = SignupItemRepository()
candidate_repo = InterviewCandidateRepository()
interview_record_repo = InterviewRecordRepository()
admission_result_repo = AdmissionResultRepository()
notification_repo = NotificationRepository()
ticket_repo = TicketRepository()
ticket_reply_repo = TicketReplyRepository()
faq_repo = FAQRepository()
user_account_repo = UserAccountRepository()
club_position_repo = ClubPositionRepository()


# ==================== 报名管理 ====================

@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """创建报名申请"""
    # 验证招新场次是否存在且可报名
    recruitment_session = signup_session_repo.get(session, data.recruitment_session_id)
    if not recruitment_session:
        raise HTTPException(status_code=404, detail="招新场次不存在")

    if recruitment_session.is_deleted == 1:
        raise HTTPException(status_code=400, detail="招新场次已删除")

    # 验证岗位是否存在且属于该社团
    positions = []
    for pos_id in data.position_ids:
        pos = club_position_repo.get(session, pos_id)
        if not pos:
            raise HTTPException(status_code=404, detail=f"岗位 {pos_id} 不存在")
        if pos.club_id != recruitment_session.club_id:
            raise HTTPException(status_code=400, detail=f"岗位 {pos_id} 不属于该社团")
        positions.append({"id": pos.id, "name": pos.name})

    # 检查是否已经报名过该场次
    existing = (
        session.query(SignupSession)
        .where(SignupSession.user_id == current_user.id)
        .where(SignupSession.recruitment_session_id == data.recruitment_session_id)
        .where(SignupSession.is_deleted == 0)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="您已经报名过该招新场次")

    # 创建报名记录
    import json
    signup = SignupSession(
        user_id=current_user.id,
        recruitment_session_id=data.recruitment_session_id,
        status="PENDING",
        self_intro=data.self_intro,
        extra_fields_json=json.dumps(data.extra_fields) if data.extra_fields else None,
    )
    session.add(signup)
    session.commit()
    session.refresh(signup)

    # 关联岗位
    for pos_id in data.position_ids:
        signup_pos = SignupItem(
            signup_session_id=signup.id,
            position_id=pos_id,
        )
        session.add(signup_pos)

    session.commit()

    # 构建响应
    response = ApplicationResponse(
        id=signup.id,
        user_id=signup.user_id,
        recruitment_session_id=signup.recruitment_session_id,
        self_intro=signup.self_intro,
        extra_fields_json=signup.extra_fields_json,
        status=signup.status,
        audit_user_id=signup.audit_user_id,
        audit_time=signup.audit_time,
        audit_reason=signup.audit_reason,
        created_at=signup.created_at,
        updated_at=signup.updated_at,
        positions=positions,
        attachments=[],
    )
    return response


@router.get("/applications/my", response_model=List[ApplicationResponse])
def get_my_applications(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取我的报名列表"""
    stmt = (
        session.query(SignupSession)
        .where(SignupSession.user_id == current_user.id)
        .where(SignupSession.is_deleted == 0)
        .order_by(SignupSession.created_at.desc())
    )
    signups = stmt.all()

    result = []
    for signup in signups:
        # 获取关联的岗位
        pos_stmt = (
            session.query(SignupItem, ClubPosition)
            .join(ClubPosition, SignupItem.position_id == ClubPosition.id)
            .where(SignupItem.signup_session_id == signup.id)
        )
        positions = [{"id": pos.id, "name": pos.name} for _, pos in pos_stmt.all()]

        result.append(ApplicationResponse(
            id=signup.id,
            user_id=signup.user_id,
            recruitment_session_id=signup.recruitment_session_id,
            self_intro=signup.self_intro,
            extra_fields_json=signup.extra_fields_json,
            status=signup.status,
            audit_user_id=signup.audit_user_id,
            audit_time=signup.audit_time,
            audit_reason=signup.audit_reason,
            created_at=signup.created_at,
            updated_at=signup.updated_at,
            positions=positions,
            attachments=[],
        ))

    return result


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application_detail(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取报名详情（旧版，保留兼容）"""
    signup = signup_session_repo.get(session, application_id)
    if not signup:
        raise HTTPException(status_code=404, detail="报名记录不存在")

    # 权限检查
    if signup.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问他人的报名记录")

    # 获取关联的岗位
    pos_stmt = (
        session.query(SignupItem, ClubPosition)
        .join(ClubPosition, SignupItem.position_id == ClubPosition.id)
        .where(SignupItem.signup_session_id == signup.id)
    )
    positions = [{"id": pos.id, "name": pos.name} for _, pos in pos_stmt.all()]

    return ApplicationResponse(
        id=signup.id,
        user_id=signup.user_id,
        recruitment_session_id=signup.recruitment_session_id,
        self_intro=signup.self_intro,
        extra_fields_json=signup.extra_fields_json,
        status=signup.status,
        audit_user_id=signup.audit_user_id,
        audit_time=signup.audit_time,
        audit_reason=signup.audit_reason,
        created_at=signup.created_at,
        updated_at=signup.updated_at,
        positions=positions,
        attachments=[],
    )


@router.put("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    data: ApplicationUpdate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """更新报名申请"""
    signup = signup_session_repo.get(session, application_id)
    if not signup:
        raise HTTPException(status_code=404, detail="报名记录不存在")

    # 权限检查
    if signup.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人的报名记录")

    # 只有PENDING状态可以修改
    if signup.status != "PENDING":
        raise HTTPException(status_code=400, detail="只有待审核状态可以修改")

    # 更新字段
    if data.self_intro is not None:
        signup.self_intro = data.self_intro
    if data.extra_fields is not None:
        import json
        signup.extra_fields_json = json.dumps(data.extra_fields)

    # 更新岗位
    if data.position_ids is not None:
        # 删除旧的岗位关联
        session.query(SignupItem).where(
            SignupItem.signup_session_id == signup.id
        ).delete()

        # 添加新的岗位关联
        for pos_id in data.position_ids:
            pos = club_position_repo.get(session, pos_id)
            if not pos or pos.club_id != signup.recruitment_session.club_id:
                raise HTTPException(status_code=400, detail=f"岗位 {pos_id} 不属于该社团")
            signup_pos = SignupItem(
                signup_session_id=signup.id,
                position_id=pos_id,
            )
            session.add(signup_pos)

    session.add(signup)
    session.commit()
    session.refresh(signup)

    # 获取关联的岗位
    pos_stmt = (
        session.query(SignupItem, ClubPosition)
        .join(ClubPosition, SignupItem.position_id == ClubPosition.id)
        .where(SignupItem.signup_session_id == signup.id)
    )
    positions = [{"id": pos.id, "name": pos.name} for _, pos in pos_stmt.all()]

    return ApplicationResponse(
        id=signup.id,
        user_id=signup.user_id,
        recruitment_session_id=signup.recruitment_session_id,
        self_intro=signup.self_intro,
        extra_fields_json=signup.extra_fields_json,
        status=signup.status,
        audit_user_id=signup.audit_user_id,
        audit_time=signup.audit_time,
        audit_reason=signup.audit_reason,
        created_at=signup.created_at,
        updated_at=signup.updated_at,
        positions=positions,
        attachments=[],
    )


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """取消报名申请"""
    signup = signup_session_repo.get(session, application_id)
    if not signup:
        raise HTTPException(status_code=404, detail="报名记录不存在")

    # 权限检查
    if signup.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权取消他人的报名记录")

    # 只有PENDING状态可以取消
    if signup.status != "PENDING":
        raise HTTPException(status_code=400, detail="只有待审核状态可以取消")

    # 软删除
    signup.is_deleted = 1
    signup.status = "CANCELLED"
    session.add(signup)
    session.commit()


# ==================== 报名管理（新版接口） ====================

# ==================== 面试管理 ====================

@router.get("/interviews/my", response_model=List[InterviewResponse])
def get_my_interviews(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取我的面试列表（旧版，保留兼容）"""
    candidates = candidate_repo.get_by_candidate_user(session, current_user.id)

    result = []
    for candidate in candidates:
        # 获取面试记录
        records = interview_record_repo.get_by_candidate(session, candidate.id)
        for record in records:
            result.append(InterviewResponse(
                id=record.id,
                session_id=candidate.session_id,
                signup_session_id=candidate.signup_session_id,
                candidate_user_id=candidate.candidate_user_id,
                planned_start_time=candidate.planned_start_time,
                planned_end_time=candidate.planned_end_time,
                actual_start_time=record.actual_start_time,
                actual_end_time=record.actual_end_time,
                status=record.status,
                final_score=record.final_score,
                created_at=record.created_at,
                updated_at=record.updated_at,
            ))

    return result


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview_detail(
    interview_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取面试详情（旧版，保留兼容）"""
    record = interview_record_repo.get(session, interview_id)
    if not record:
        raise HTTPException(status_code=404, detail="面试记录不存在")

    # 获取候选人信息
    candidate = candidate_repo.get_by_candidate_and_session(
        session, record.candidate_user_id, record.session_id
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人记录不存在")

    # 权限检查
    if candidate.candidate_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问他人的面试记录")

    return InterviewResponse(
        id=record.id,
        session_id=candidate.session_id,
        signup_session_id=candidate.signup_session_id,
        candidate_user_id=candidate.candidate_user_id,
        planned_start_time=candidate.planned_start_time,
        planned_end_time=candidate.planned_end_time,
        actual_start_time=record.actual_start_time,
        actual_end_time=record.actual_end_time,
        status=record.status,
        final_score=record.final_score,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.put("/interviews/{interview_id}/confirmation", response_model=InterviewResponse)
def update_interview_confirmation(
    interview_id: int,
    data: InterviewConfirmationUpdate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """确认/拒绝面试"""
    record = interview_record_repo.get(session, interview_id)
    if not record:
        raise HTTPException(status_code=404, detail="面试记录不存在")

    # 获取候选人信息
    candidate = candidate_repo.get_by_candidate_and_session(
        session, record.candidate_user_id, record.session_id
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人记录不存在")

    # 权限检查
    if candidate.candidate_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人的面试记录")

    # 只有SCHEDULED状态可以确认
    if record.status != "SCHEDULED":
        raise HTTPException(status_code=400, detail="只有已排期状态可以确认")

    if data.status not in ["CONFIRMED", "DECLINED"]:
        raise HTTPException(status_code=400, detail="状态只能是 CONFIRMED 或 DECLINED")

    record.status = data.status
    session.add(record)
    session.commit()
    session.refresh(record)

    return InterviewResponse(
        id=record.id,
        session_id=candidate.session_id,
        signup_session_id=candidate.signup_session_id,
        candidate_user_id=candidate.candidate_user_id,
        planned_start_time=candidate.planned_start_time,
        planned_end_time=candidate.planned_end_time,
        actual_start_time=record.actual_start_time,
        actual_end_time=record.actual_end_time,
        status=record.status,
        final_score=record.final_score,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/interviews/{interview_id}/result", response_model=InterviewResultResponse)
def get_interview_result(
    interview_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取面试结果"""
    record = interview_record_repo.get(session, interview_id)
    if not record:
        raise HTTPException(status_code=404, detail="面试记录不存在")

    # 获取候选人信息
    candidate = candidate_repo.get_by_candidate_and_session(
        session, record.candidate_user_id, record.session_id
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人记录不存在")

    # 权限检查
    if candidate.candidate_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问他人的面试结果")

    # 只有COMPLETED状态可以查看结果
    if record.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="面试尚未完成")

    # 获取录取结果
    admission = admission_result_repo.get_by_candidate(session, candidate.candidate_user_id)

    passed = admission.result_status == "ADMITTED" if admission else False

    return InterviewResultResponse(
        passed=passed,
        score=record.final_score,
        feedback=record.remarks,
        admission_result=admission.result_status if admission else None,
    )


# ==================== 通知管理 ====================

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取通知列表"""
    notifications = notification_repo.get_by_user(session, current_user.id, unread_only)

    result = []
    for notification in notifications:
        result.append(NotificationResponse(
            id=notification.id,
            type=notification.type,
            title=notification.title,
            content=notification.content,
            biz_id=notification.biz_id,
            sent_at=notification.sent_at,
            created_at=notification.created_at,
        ))

    return result


@router.put("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_as_read(
    notification_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """标记通知为已读"""
    notification = notification_repo.get(session, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    # 检查用户是否有该通知
    stmt = (
        session.query(NotificationUser)
        .where(NotificationUser.notification_id == notification_id)
        .where(NotificationUser.user_id == current_user.id)
        .where(NotificationUser.is_deleted == 0)
    )
    nu = stmt.first()
    if not nu:
        raise HTTPException(status_code=403, detail="无权访问该通知")

    notification_repo.mark_as_read(session, notification_id, current_user.id)


@router.put("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_as_read(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """标记所有通知为已读"""
    notification_repo.mark_all_as_read(session, current_user.id)


@router.get("/notifications/count", response_model=NotificationUnreadCountResponse)
def get_unread_notification_count(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取未读通知数量"""
    count = notification_repo.get_unread_count(session, current_user.id)
    return NotificationUnreadCountResponse(count=count)


# ==================== 工单管理 ====================

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """创建工单"""
    ticket = Ticket(
        user_id=current_user.id,
        club_id=data.club_id,
        title=data.title,
        category=data.category,
        content=data.content,
        status="OPEN",
        priority="NORMAL",
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return TicketResponse(
        id=ticket.id,
        user_id=ticket.user_id,
        club_id=ticket.club_id,
        title=ticket.title,
        category=ticket.category,
        content=ticket.content,
        status=ticket.status,
        priority=ticket.priority,
        assignee_id=ticket.assignee_id,
        resolved_at=ticket.resolved_at,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        replies=[],
    )


@router.get("/tickets/my", response_model=List[TicketResponse])
def get_my_tickets(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取我的工单列表"""
    tickets = ticket_repo.get_by_user(session, current_user.id)

    result = []
    for ticket in tickets:
        # 获取回复
        replies = ticket_reply_repo.get_by_ticket(session, ticket.id)
        reply_list = [
            {
                "id": r.id,
                "ticket_id": r.ticket_id,
                "user_id": r.user_id,
                "content": r.content,
                "is_from_staff": r.is_from_staff,
                "attachment_url": r.attachment_url,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in replies
        ]

        result.append(TicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            club_id=ticket.club_id,
            title=ticket.title,
            category=ticket.category,
            content=ticket.content,
            status=ticket.status,
            priority=ticket.priority,
            assignee_id=ticket.assignee_id,
            resolved_at=ticket.resolved_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            replies=reply_list,
        ))

    return result


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取工单详情"""
    ticket = ticket_repo.get(session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问他人的工单")

    # 获取回复
    replies = ticket_reply_repo.get_by_ticket(session, ticket.id)
    reply_list = [
        {
            "id": r.id,
            "ticket_id": r.ticket_id,
            "user_id": r.user_id,
            "content": r.content,
            "is_from_staff": r.is_from_staff,
            "attachment_url": r.attachment_url,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in replies
    ]

    return TicketResponse(
        id=ticket.id,
        user_id=ticket.user_id,
        club_id=ticket.club_id,
        title=ticket.title,
        category=ticket.category,
        content=ticket.content,
        status=ticket.status,
        priority=ticket.priority,
        assignee_id=ticket.assignee_id,
        resolved_at=ticket.resolved_at,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        replies=reply_list,
    )


@router.post("/tickets/{ticket_id}/messages", response_model=TicketReplyResponse, status_code=status.HTTP_201_CREATED)
def add_ticket_message(
    ticket_id: int,
    data: TicketMessageCreate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """添加工单回复"""
    ticket = ticket_repo.get(session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权回复他人的工单")

    reply = TicketReply(
        ticket_id=ticket_id,
        user_id=current_user.id,
        content=data.content,
        is_from_staff=False,
        attachment_url=data.attachment_url,
    )
    session.add(reply)
    session.commit()
    session.refresh(reply)

    return TicketReplyResponse(
        id=reply.id,
        ticket_id=reply.ticket_id,
        user_id=reply.user_id,
        content=reply.content,
        is_from_staff=reply.is_from_staff,
        attachment_url=reply.attachment_url,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
    )


# ==================== 个人中心 ====================

@router.get("/students/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: UserAccount = Depends(get_current_user),
):
    """获取学生个人资料"""
    return StudentProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        name=current_user.name,
        id_card_no=current_user.id_card_no,
        school_code=current_user.school_code,
        major=current_user.major,
        student_no=current_user.student_no,
        avatar_url=current_user.avatar_url,
        email=current_user.email,
        is_verified_campus=current_user.is_verified_campus,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/students/profile", response_model=StudentProfileResponse)
def update_student_profile(
    data: StudentProfileUpdate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """更新学生个人资料"""
    if data.name is not None:
        current_user.name = data.name
    if data.email is not None:
        current_user.email = data.email
    if data.major is not None:
        current_user.major = data.major

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return StudentProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        name=current_user.name,
        id_card_no=current_user.id_card_no,
        school_code=current_user.school_code,
        major=current_user.major,
        student_no=current_user.student_no,
        avatar_url=current_user.avatar_url,
        email=current_user.email,
        is_verified_campus=current_user.is_verified_campus,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get("/students/applications/stats", response_model=ApplicationStatsResponse)
def get_application_stats(
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """获取报名统计"""
    stmt = (
        session.query(SignupSession)
        .where(SignupSession.user_id == current_user.id)
        .where(SignupSession.is_deleted == 0)
    )
    all_signups = stmt.all()

    total = len(all_signups)
    pending = sum(1 for s in all_signups if s.status == "PENDING")
    approved = sum(1 for s in all_signups if s.status == "APPROVED")
    rejected = sum(1 for s in all_signups if s.status == "REJECTED")

    return ApplicationStatsResponse(
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
    )


