from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.school import router as school_router
from app.api.v1.club import router as club_router
from app.api.v1.admin_compat import router as admin_compat_router
from app.api.v1.interviewer_invitation import router as interviewer_invitation_router
from app.api.v1.department import router as department_router
from app.api.v1.position import router as position_router
from app.api.v1.recruitment_session import router as recruitment_router
from app.api.v1.signup import router as signup_router
from app.api.v1.interview import router as interview_router
from app.api.v1.statistics import router as statistics_router
from app.api.v1.student import router as student_router
from app.api.v1.system import router as system_router
from app.db.init_db import check_and_sync_db
from sqlalchemy.exc import SQLAlchemyError
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时检查数据库，关闭时不做额外操作"""
    try:
        check_and_sync_db()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        raise
    yield


app = FastAPI(
    title=settings.app_name,
    description="校园社团招新与面试管理系统",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS 配置
# 生产环境建议将 allow_origins 配置为前端域名
# 演示环境可暂时允许所有来源 ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，方便演示部署
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 全局异常处理 ============

logger = logging.getLogger(__name__)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库异常，避免暴露敏感信息"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "数据库操作失败，请稍后重试"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    # 在开发环境返回详细错误信息，生产环境返回通用错误
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"内部服务器错误: {str(exc)}"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "内部服务器错误，请稍后重试"},
        )

# ============ 路由注册 ============

app.include_router(auth_router, prefix="/api")
app.include_router(school_router, prefix="/api")
app.include_router(admin_compat_router, prefix="/api")
app.include_router(club_router, prefix="/api")
app.include_router(interviewer_invitation_router, prefix="/api")
app.include_router(department_router, prefix="/api")
app.include_router(position_router, prefix="/api")
app.include_router(recruitment_router, prefix="/api")
app.include_router(signup_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(statistics_router, prefix="/api")
app.include_router(student_router, prefix="/api")
app.include_router(system_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "env": settings.app_env
    }
