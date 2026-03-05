"""
初始化存儲桶目錄結構

運行此腳本測試 RustFS 連接並創建目錄結構
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.storage import get_storage_service


def init_storage_structure():
    """初始化存儲目錄結構"""
    service = get_storage_service()

    print(f"存儲服務: {service.bucket}")
    print(f"環境: {service.env}")
    print(f"Endpoint: {settings.storage_endpoint}")
    print("-" * 50)

    # 測試連接
    success, message = service.test_connection()
    print(f"連接測試: {message}")

    if not success:
        print("\n⚠️  存儲服務不可用，請檢查:")
        print("  1. RustFS 容器是否運行")
        print("  2. Bucket 是否已創建")
        print("  3. 認證信息是否正確")
        return False

    # 目錄結構定義
    directories = [
        # 用戶相關
        ("avatars",),

        # 社團相關
        ("clubs", "logos"),
        ("clubs", "certs"),

        # 面試相關
        ("interviews", "recordings"),
        ("interviews", "attachments"),
    ]

    print("\n創建目錄結構...")
    for paths in directories:
        prefix = service.ensure_directory(*paths)
        print(f"  ✓ {prefix}")

    print(f"\n✓ 初始化完成！")
    return True


if __name__ == "__main__":
    init_storage_structure()
