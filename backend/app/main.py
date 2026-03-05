from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.school import router as school_router
from app.api.v1.club import router as club_router
from app.api.v1.department import router as department_router
from app.api.v1.position import router as position_router
from app.api.v1.recruitment_session import router as recruitment_router
from app.api.v1.signup import router as signup_router
from app.api.v1.interview import router as interview_router
from app.api.v1.student import router as student_router
from app.db.session import engine
from sqlalchemy import text
from alembic.config import Config
from alembic import command


def run_migrations():
    """检查并运行数据库迁移"""
    try:
        # 测试数据库连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # 执行迁移
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("数据库迁移完成")
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        raise

app = FastAPI(
    title=settings.app_name,
    description="校园社团招新与面试管理系统",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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

app.include_router(auth_router, prefix="/api")
app.include_router(school_router, prefix="/api")
app.include_router(club_router, prefix="/api")
app.include_router(department_router, prefix="/api")
app.include_router(position_router, prefix="/api")
app.include_router(recruitment_router, prefix="/api")
app.include_router(signup_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(student_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "env": settings.app_env
    }


@app.on_event("startup")
def startup():
    """启动时自动执行数据库迁移"""
    # 建议生产环境注释掉自动迁移，改为手动执行 alembic upgrade head
    # 避免因数据库连接延迟导致启动失败
    pass
    # if settings.app_env == "production":
    #     run_migrations()
