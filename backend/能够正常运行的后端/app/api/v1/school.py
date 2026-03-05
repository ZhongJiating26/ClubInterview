from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.school import SchoolRepository
from app.schemas.school import SchoolSearchResponse, SchoolItem


router = APIRouter(prefix="/schools", tags=["School"])
school_repo = SchoolRepository()


@router.get("/search", response_model=SchoolSearchResponse)
def search_schools(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词"),
    limit: int = Query(default=20, ge=1, le=50, description="返回数量限制"),
    session: Session = Depends(get_session),
):
    """
    学校搜索接口

    根据关键词模糊搜索学校，返回匹配的学校列表。

    ## 使用示例
    ```
    GET /api/v1/schools/search?q=浙江
    ```

    ## 响应示例
    ```json
    {
      "total": 2,
      "items": [
        {"id": 1, "name": "浙江大学", "code": "4111010103"},
        {"id": 2, "name": "浙江工业大学", "code": "4111031035"}
      ]
    }
    ```
    """
    schools = school_repo.search_by_name(session, keyword=q, limit=limit)

    return SchoolSearchResponse(
        total=len(schools),
        items=[
            SchoolItem(id=s.id, name=s.name, code=s.code)
            for s in schools
        ],
    )
