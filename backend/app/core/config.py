from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # ===== 基础 =====
    app_name: str = Field(default="Club Interview System")
    app_env: str = Field(default="dev")
    debug: bool = Field(default=False)

    # ===== 数据库 =====
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = ""

    # ===== JWT =====
    jwt_secret_key: str = Field("CHANGE_ME", description="JWT密钥")
    jwt_algorithm: str = Field("HS256")
    jwt_expire_minutes: int = Field(60 * 24)  # 1天
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ===== 存储 (RustFS/S3) =====
    storage_provider: str = Field("local", description="存储提供商: rustfs, local")
    storage_endpoint: str = Field("", description="存储 endpoint (服务器连接用)")
    storage_public_endpoint: str = Field("", description="存储公开 endpoint (返回给前端的URL，可使用局域网IP)")
    storage_access_key: str = Field("", description="访问密钥")
    storage_secret_key: str = Field("", description="密钥")
    storage_bucket: str = Field("", description="存储桶名称")
    storage_env: str = Field("dev", description="环境标识")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# 全局唯一配置对象
settings = Settings()
