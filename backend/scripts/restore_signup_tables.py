"""
恢复被误删的报名相关表
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def restore_signup_tables():
    """恢复报名相关的表"""

    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "campus_club_interview"),
        charset='utf8mb4'
    )

    try:
        with connection.cursor() as cursor:
            # 检查表是否已存在
            cursor.execute("SHOW TABLES LIKE 'signup_session'")
            if cursor.fetchone():
                print("报名表已存在，无需恢复")
                return

            print("开始恢复报名相关表...")

            # 创建 recruitment_session 表
            cursor.execute("""
                CREATE TABLE recruitment_session (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    club_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    max_candidates INTEGER,
                    status VARCHAR(20) DEFAULT 'DRAFT',
                    created_by INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_recruitment_session_is_deleted (is_deleted)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ recruitment_session 表创建成功")

            # 创建 recruitment_session_position 表
            cursor.execute("""
                CREATE TABLE recruitment_session_position (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    session_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    position_name VARCHAR(100) NOT NULL,
                    position_description TEXT,
                    position_requirement TEXT,
                    recruit_quota INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_recruitment_session_position_is_deleted (is_deleted)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ recruitment_session_position 表创建成功")

            # 创建 signup_session 表
            cursor.execute("""
                CREATE TABLE signup_session (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    recruitment_session_id INTEGER NOT NULL,
                    self_intro TEXT,
                    extra_fields_json TEXT,
                    status VARCHAR(20) DEFAULT 'PENDING',
                    audit_user_id INTEGER,
                    audit_time DATETIME,
                    audit_reason VARCHAR(255),
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_signup_session_is_deleted (is_deleted),
                    INDEX ix_signup_session_user_id (user_id),
                    INDEX ix_signup_session_recruitment_session_id (recruitment_session_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ signup_session 表创建成功")

            # 创建 signup_item 表
            cursor.execute("""
                CREATE TABLE signup_item (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    signup_session_id INTEGER NOT NULL,
                    department_id INTEGER,
                    position_id INTEGER NOT NULL,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_signup_item_is_deleted (is_deleted),
                    INDEX ix_signup_item_signup_session_id (signup_session_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ signup_item 表创建成功")

            # 创建 signup_attachment 表
            cursor.execute("""
                CREATE TABLE signup_attachment (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    signup_session_id INTEGER NOT NULL,
                    file_url VARCHAR(255) NOT NULL,
                    file_type VARCHAR(20) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_signup_attachment_is_deleted (is_deleted),
                    INDEX ix_signup_attachment_signup_session_id (signup_session_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ signup_attachment 表创建成功")

            # 创建 department 表
            cursor.execute("""
                CREATE TABLE department (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    club_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_department_is_deleted (is_deleted)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ department 表创建成功")

            # 创建 club_position 表
            cursor.execute("""
                CREATE TABLE club_position (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    club_id INTEGER NOT NULL,
                    department_id INTEGER,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    requirement TEXT,
                    created_at DATETIME,
                    updated_at DATETIME,
                    is_deleted TINYINT DEFAULT 0,
                    deleted_at DATETIME,
                    PRIMARY KEY (id),
                    INDEX ix_club_position_is_deleted (is_deleted)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✓ club_position 表创建成功")

        connection.commit()
        print("\n所有表恢复成功！")

    except Exception as e:
        connection.rollback()
        print(f"\n恢复失败: {e}")
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    restore_signup_tables()
