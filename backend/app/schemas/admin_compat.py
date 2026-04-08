from pydantic import BaseModel, Field


class AdminUserSearchItem(BaseModel):
    id: int
    name: str | None = None
    phone: str


class AdminUserSearchResponse(BaseModel):
    items: list[AdminUserSearchItem]
    total: int


class InviteInterviewerRequest(BaseModel):
    user_id: int = Field(..., description="被邀请用户ID")


class InterviewerInvitationResponse(BaseModel):
    id: int
    club_id: int
    club_name: str
    club_logo_url: str | None = None
    user_id: int
    inviter_name: str | None = None
    status: str
    invite_code: str
    created_at: str


class RejectInvitationRequest(BaseModel):
    reason: str | None = Field(default=None, description="拒绝理由")
