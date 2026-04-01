"""
数据库启动检查与初始化模块

在每次后端启动时自动检查数据库表结构，创建缺失的表，
并保证 role 和 school 表带有固定初始数据。
"""

import logging
import sys
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.sql.sqltypes import Integer

from app.db.session import engine
from app.db.schools_data import SCHOOL_DATA

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

# 角色固定数据
ROLE_DATA = [
    (1, "ADMIN", "系统管理员", "拥有所有权限的平台管理员"),
    (2, "CLUB_ADMIN", "社团管理员", "社团管理员，可管理社团相关业务"),
    (3, "INTERVIEWER", "面试官", "面试官，可参与面试评分"),
    (4, "STUDENT", "普通学生", "普通学生用户"),
]

# 需要在重建后插入初始数据的表
FIXED_DATA_TABLES = {
    "role": ROLE_DATA,
    "school": SCHOOL_DATA,
}


def _import_all_models() -> list[type]:
    """导入所有模型以注册到 SQLModel.metadata，并返回模型类列表"""
    # noqa: F401 - 导入所有模型类以注册表
    from app.models.admission_result import AdmissionResult  # noqa: F401
    from app.models.club import Club  # noqa: F401
    from app.models.club_position import ClubPosition  # noqa: F401
    from app.models.department import Department  # noqa: F401
    from app.models.faq import FAQ  # noqa: F401
    from app.models.interview_candidate import InterviewCandidate  # noqa: F401
    from app.models.interview_record import InterviewRecord  # noqa: F401
    from app.models.interview_score import InterviewScore  # noqa: F401
    from app.models.interview_session import InterviewSession  # noqa: F401
    from app.models.interview_session_interviewer import InterviewSessionInterviewer  # noqa: F401
    from app.models.interview_session_score_item import InterviewSessionScoreItem  # noqa: F401
    from app.models.notification import Notification  # noqa: F401
    from app.models.notification_user import NotificationUser  # noqa: F401
    from app.models.recruitment_session import RecruitmentSession  # noqa: F401
    from app.models.recruitment_session_position import RecruitmentSessionPosition  # noqa: F401
    from app.models.role import Role  # noqa: F401
    from app.models.school import School  # noqa: F401
    from app.models.score_item import ScoreItem  # noqa: F401
    from app.models.score_template import ScoreTemplate  # noqa: F401
    from app.models.signup_attachment import SignupAttachment  # noqa: F401
    from app.models.signup_item import SignupItem  # noqa: F401
    from app.models.signup_session import SignupSession  # noqa: F401
    from app.models.ticket import Ticket, TicketReply  # noqa: F401
    from app.models.user_account import UserAccount  # noqa: F401
    from app.models.user_role import UserRole  # noqa: F401
    from app.models.verification_code import VerificationCode  # noqa: F401

    return [
        AdmissionResult,
        Club,
        ClubPosition,
        Department,
        FAQ,
        InterviewCandidate,
        InterviewRecord,
        InterviewScore,
        InterviewSession,
        InterviewSessionInterviewer,
        InterviewSessionScoreItem,
        Notification,
        NotificationUser,
        RecruitmentSession,
        RecruitmentSessionPosition,
        Role,
        School,
        ScoreItem,
        ScoreTemplate,
        SignupAttachment,
        SignupItem,
        SignupSession,
        Ticket,
        TicketReply,
        UserAccount,
        UserRole,
        VerificationCode,
    ]


def _create_table_sql(table_name: str, model_cls: type) -> str:
    """生成 CREATE TABLE SQL 语句"""
    # 获取模型的所有列
    columns = []
    unique_columns: set[str] = set()
    index_columns: list[str] = []
    primary_keys = [col.key for col in model_cls.__mapper__.primary_key]

    for col in model_cls.__mapper__.columns:
        col_def = f"`{col.key}` {col.type}"
        if not col.nullable:
            col_def += " NOT NULL"
        # SQLModel 的整型单主键通常依赖数据库默认自增策略，这里显式补齐 MySQL 的 AUTO_INCREMENT
        if (
            col.autoincrement is True
            or (
                col.primary_key
                and len(primary_keys) == 1
                and isinstance(col.type, Integer)
            )
        ):
            col_def += " AUTO_INCREMENT"
        if col.default is not None and hasattr(col.default, 'arg'):
            default_val = col.default.arg
            if not callable(default_val):
                if isinstance(default_val, bool):
                    col_def += f" DEFAULT {1 if default_val else 0}"
                elif isinstance(default_val, str):
                    col_def += f" DEFAULT '{default_val}'"
                else:
                    col_def += f" DEFAULT {default_val}"
        if col.unique:
            unique_columns.add(col.key)
        if col.index:
            index_columns.append(col.key)
        columns.append(col_def)

    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
    sql += ",\n".join(f"  {col}" for col in columns)
    if primary_keys:
        sql += f",\n  PRIMARY KEY ({', '.join(f'`{pk}`' for pk in primary_keys)})"
    for col_name in unique_columns:
        sql += f",\n  UNIQUE (`{col_name}`)"
    for col_name in index_columns:
        sql += f",\n  INDEX (`{col_name}`)"
    sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci"
    return sql


def _insert_fixed_data(table_name: str, conn) -> None:
    """插入固定数据到指定表"""
    if table_name not in FIXED_DATA_TABLES:
        return

    data = FIXED_DATA_TABLES[table_name]
    if table_name == "role":
        for row in data:
            id_, code, name, desc = row
            conn.execute(
                text(
                    "INSERT INTO `role` (id, code, name, description, created_at, updated_at, is_deleted, deleted_at) "
                    "VALUES (:id, :code, :name, :desc, :now, :now, 0, NULL)"
                ),
                {"id": id_, "code": code, "name": name, "desc": desc, "now": datetime.utcnow()},
            )

    elif table_name == "school":
        # 分批插入以避免 SQL 语句过长
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            values_parts = []
            params = {}
            for idx, (id_, name, code) in enumerate(batch):
                values_parts.append(f"(:id_{idx}, :name_{idx}, :code_{idx}, :now, :now, 0, NULL)")
                params[f"id_{idx}"] = id_
                params[f"name_{idx}"] = name
                params[f"code_{idx}"] = code
            params["now"] = datetime.utcnow()

            sql = (
                "INSERT INTO `school` (id, name, code, created_at, updated_at, is_deleted, deleted_at) "
                f"VALUES {', '.join(values_parts)}"
            )
            conn.execute(text(sql), params)


def check_and_sync_db() -> None:
    """
    检查并同步数据库结构

    遍历所有模型，对每张表：
    - 表不存在 → CREATE TABLE + 插入固定数据
    - 表已存在 → 跳过（列比较逻辑不可靠，避免误判）
    """
    all_model_classes = _import_all_models()

    from sqlalchemy import inspect as _inspect
    inspector = _inspect(engine)
    existing_tables = set(inspector.get_table_names())

    checked: list[str] = []
    created: list[str] = []

    for model_cls in all_model_classes:
        if not hasattr(model_cls, "__table__"):
            continue

        table_name = model_cls.__tablename__
        checked.append(table_name)

        if table_name not in existing_tables:
            create_sql = _create_table_sql(table_name, model_cls)
            with engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            created.append(table_name)

            with engine.connect() as conn:
                _insert_fixed_data(table_name, conn)
                conn.commit()

    # 日志输出
    logger.info(f"数据库检查完成，共 {len(checked)} 个表")
    if created:
        logger.warning(f"  新建表 ({len(created)}): {', '.join(created)}")
    else:
        logger.info("  表结构检查正常")
