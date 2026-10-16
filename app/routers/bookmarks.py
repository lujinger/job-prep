from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate, BookmarkOut
from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

#  ---------- 创建，加上认证 ----------

@router.post("/", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 新增：需要登录
):
    obj = Bookmark(title=payload.title, url=payload.url)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # 统一把datetime转字符串，避免前端收到复杂对象
    return BookmarkOut(
        id=obj.id,
        title=obj.title,
        url=obj.url,
        created_at=obj.created_at.isoformat() if obj.created_at else "",
    )


# ---------- 列表查询 ----------

@router.get("/", response_model=List[BookmarkOut])
def list_bookmarks(
    skip: int = Query(0, ge=0, description="跳过前N条"),
    limit: int = Query(10, ge=1, le=100, description="返回最多N条"),
    q: str = Query(None, min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(Bookmark)

    # 搜索过滤
    if q:
        query = query.filter(Bookmark.title.contains(q))

    # 排序 + 分页
    items = query.order_by(Bookmark.created_at.desc()).offset(skip).limit(limit).all()
    # items = db.query(Bookmark).order_by(Bookmark.created_at.desc()).all()

    # 手动转成 BookmarkOut 列表（和前面的 create_bookmark 保持一致，created_at 转字符串）
    return [
        BookmarkOut(
            id=i.id,
            title=i.title,
            url=i.url,
            created_at=i.created_at.isoformat() if i.created_at else "",
        )
        for i in items
    ]


# ---------- 单条查询 ----------

@router.get("/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(
        bookmark_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    item = db.get(Bookmark, bookmark_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Bookmark with id={bookmark_id} not found")
    return BookmarkOut(
        id=item.id,
        title=item.title,
        url=item.url,
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


# ---------- 更新，增加认证 ----------

@router.put("/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.get(Bookmark, bookmark_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Bookmark with id={bookmark_id} not found")

    # 逐个字段更新,只改非空字段
    if payload.title is not None:
        item.title = payload.title
    if payload.url is not None:
        item.url = payload.url
    # 注意：不更新 created_at，保持创建时间不变

    db.commit()
    db.refresh(item)
    return BookmarkOut(
        id=item.id,
        title=item.title,
        url=item.url,
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


# ---------- 删除 ----------

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.get(Bookmark, bookmark_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Bookmark with id={bookmark_id} not found")

    db.delete(item)
    db.commit()
    # 204 No Content：不返回响应体
    return None
