from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate, BookmarkOut
from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

#  ---------- 创建，绑定当前用户 ----------

@router.post("/", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = Bookmark(
        title=payload.title,
        url=payload.url,
        user_id=current_user.id,  # ← 绑定当前登录用户
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return BookmarkOut(
        id=obj.id,
        title=obj.title,
        url=obj.url,
        created_at=obj.created_at.isoformat() if obj.created_at else "",
    )


# ---------- 列表查询，只返回当前用户的 ----------

@router.get("/", response_model=List[BookmarkOut])
def list_bookmarks(
    skip: int = Query(0, ge=0, description="跳过前N条"),
    limit: int = Query(10, ge=1, le=100, description="返回最多N条"),
    q: str = Query(None, min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 只查当前用户的书签
    query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)

    # 搜索过滤（只在当前用户的书签里搜）
    if q:
        query = query.filter(Bookmark.title.contains(q))

    # 排序 + 分页
    items = query.order_by(Bookmark.created_at.desc()).offset(skip).limit(limit).all()

    return [
        BookmarkOut(
            id=i.id,
            title=i.title,
            url=i.url,
            created_at=i.created_at.isoformat() if i.created_at else "",
        )
        for i in items
    ]


# ---------- 单条查询，跨用户返回404 ----------

@router.get("/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 同时按 id + user_id 查，跨用户直接 404（不暴露存在性）
    item = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return BookmarkOut(
        id=item.id,
        title=item.title,
        url=item.url,
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


# ---------- 更新，跨用户返回404 ----------

@router.put("/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 同时按 id + user_id 查
    item = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if payload.title is not None:
        item.title = payload.title
    if payload.url is not None:
        item.url = payload.url

    db.commit()
    db.refresh(item)
    return BookmarkOut(
        id=item.id,
        title=item.title,
        url=item.url,
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


# ---------- 删除，跨用户返回404 ----------

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 同时按 id + user_id 查
    item = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(item)
    db.commit()
    return None