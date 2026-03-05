"""
存儲服務模塊 (RustFS/S3 兼容)

連接 RustFS 存儲桶，處理文件上傳、下載、目錄管理
"""
import os
import socket
import logging
from typing import Optional
from contextlib import contextmanager

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_lan_ip() -> str:
    """
    获取本机局域网 IP 地址

    通过创建 UDP socket 连接到外部地址来获取本机 IP，
    这样可以获取到实际用于网络通信的局域网 IP，
    而不是 127.0.0.1

    Returns:
        局域网 IP 地址，如 "192.168.1.100"
    """
    try:
        # 创建一个 UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接到一个外部地址（不会实际发送数据）
        s.connect(("8.8.8.8", 80))
        # 获取本机 IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # 如果获取失败，回退到 localhost
        return "127.0.0.1"


def get_storage_public_endpoint() -> str:
    """
    获取存储服务的公开访问 endpoint

    优先使用配置的 STORAGE_PUBLIC_ENDPOINT，
    否则根据 STORAGE_ENDPOINT 自动替换为局域网 IP

    Returns:
        公开访问的 endpoint URL
    """
    if settings.storage_public_endpoint:
        return settings.storage_public_endpoint

    # 如果没有配置公开 endpoint，自动生成
    if not settings.storage_endpoint:
        return ""

    # 解析 endpoint，提取端口
    try:
        from urllib.parse import urlparse
        parsed = urlparse(settings.storage_endpoint)
        port = parsed.port
        if port is None:
            port = 9000  # 默认端口

        # 获取局域网 IP
        lan_ip = get_lan_ip()

        # 拼接新的 endpoint
        return f"http://{lan_ip}:{port}"
    except Exception:
        return settings.storage_endpoint


class StorageService:
    """存儲服務類"""

    def __init__(self):
        self.bucket = settings.storage_bucket
        self.env = settings.storage_env
        self._s3_client: Optional[boto3.client] = None
        self._initialized = False

    def _get_s3_client(self) -> boto3.client:
        """延遲初始化 S3 客戶端"""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.storage_endpoint,
                aws_access_key_id=settings.storage_access_key,
                aws_secret_access_key=settings.storage_secret_key,
                region_name="us-east-1",
                config=Config(
                    signature_version="s3v4",
                    retries={"max_attempts": 3},
                ),
            )
            self._initialized = True
        return self._s3_client

    @property
    def s3_client(self) -> boto3.client:
        """獲取 S3 客戶端"""
        return self._get_s3_client()

    def test_connection(self) -> tuple[bool, str]:
        """
        測試存儲服務連接

        Returns:
            (是否成功, 消息)
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            return True, f"連接成功，Bucket: {self.bucket}"
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ["404", "NoSuchBucket"]:
                # 嘗試創建 bucket
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket)
                    return True, f"Bucket '{self.bucket}' 創建成功"
                except ClientError as create_err:
                    return False, f"Bucket 不存在且創建失敗: {create_err}"
            return False, f"連接失敗: {e}"

    def ensure_bucket(self) -> bool:
        """
        確保 bucket 存在

        Returns:
            是否成功
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ["404", "NoSuchBucket"]:
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket)
                    logger.info(f"Bucket '{self.bucket}' 創建成功")
                    return True
                except ClientError as e:
                    logger.error(f"創建 Bucket 失敗: {e}")
                    return False
            return False

    def _get_prefix(self, *paths: str) -> str:
        """生成前綴路徑"""
        parts = [self.env] + list(paths)
        return "/".join(p.strip("/") for p in parts) + "/"

    def ensure_directory(self, *paths: str) -> str:
        """
        確保目錄存在（創建前綴標記）

        Args:
            *paths: 目錄路徑 parts

        Returns:
            前綴路徑
        """
        prefix = self._get_prefix(*paths)
        marker_key = prefix + ".dir_marker"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=marker_key,
                Body=b"",
                ContentType="text/plain",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "PreconditionFailed":
                logger.warning(f"創建目錄標記失敗: {e}")

        return prefix

    def upload_file(
        self,
        file_path: str,
        *paths: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        上傳本地文件到存儲桶

        Args:
            file_path: 本地文件路徑
            *paths: 存儲目標路徑
            content_type: 文件 MIME 類型

        Returns:
            存儲對象的 key
        """
        prefix = self._get_prefix(*paths)
        filename = os.path.basename(file_path)
        key = prefix + filename

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        with open(file_path, "rb") as f:
            self.s3_client.upload_fileobj(
                f,
                self.bucket,
                key,
                ExtraArgs=extra_args,
            )

        return key

    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        paths: tuple[str, ...],
    ) -> str:
        """
        上傳字節數據到存儲桶

        Args:
            data: 字節數據
            filename: 文件名
            paths: 存儲目標路徑元組

        Returns:
            存儲對象的 key
        """
        prefix = self._get_prefix(*paths)
        key = prefix + filename

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=self._get_content_type(filename),
        )

        return key

    def _get_content_type(self, filename: str) -> str:
        """根據文件名獲取 content type"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def get_signed_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        生成預簽名 URL

        Args:
            key: 文件 key
            expires_in: 過期時間（秒）

        Returns:
            預簽名 URL
        """
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )

    def list_objects(
        self,
        *paths: str,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[dict]:
        """
        列出對象

        Args:
            *paths: 前綴路徑
            prefix: 額外前綴
            max_keys: 最大數量

        Returns:
            對象列表
        """
        path_prefix = self._get_prefix(*paths) + prefix

        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=path_prefix,
            MaxKeys=max_keys,
        )

        return response.get("Contents", [])

    def delete_object(self, key: str) -> bool:
        """
        刪除對象

        Args:
            key: 文件 key

        Returns:
            是否成功
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_object_url(self, key: str) -> str:
        """
        獲取對象的公開 URL

        Args:
            key: 文件 key

        Returns:
            公開訪問 URL
        """
        # 自动获取公开 endpoint（优先使用配置，否则自动获取局域网 IP）
        endpoint = get_storage_public_endpoint()
        if not endpoint:
            endpoint = settings.storage_endpoint
        # 拼接公開 URL
        return f"{endpoint}/{self.bucket}/{key}"


# 延遲創建全局單例
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """獲取存儲服務實例（延遲初始化）"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service


def init_storage() -> tuple[bool, str]:
    """
    初始化存儲服務

    Returns:
        (是否成功, 消息)
    """
    service = get_storage_service()
    return service.test_connection()
