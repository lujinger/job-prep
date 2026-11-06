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
    bookmark = Bookmark(
        title=payload.title,
        url=payload.url,
        user_id=current_user.id,  # ← 绑定当前登录用户
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


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
    bookmarks_query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)

    # 搜索过滤（只在当前用户的书签里搜）
    if q:
        bookmarks_query = bookmarks_query.filter(Bookmark.title.contains(q))

    # 排序 + 分页
    bookmarks = bookmarks_query.order_by(Bookmark.created_at.desc()).offset(skip).limit(limit).all()

    return bookmarks

# ---------- 单条查询，跨用户返回404 ----------

@router.get("/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 同时按 id + user_id 查，跨用户直接 404（不暴露存在性）
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


# ---------- 更新，跨用户返回404 ----------

@router.put("/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ← 同时按 id + user_id 查
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if payload.title is not None:
        bookmark.title = payload.title
    if payload.url is not None:
        bookmark.url = payload.url

    db.commit()
    db.refresh(bookmark)
    return bookmark


# ---------- 删除，跨用户返回404 ----------

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 同时按 id + user_id 查询，跨用户直接返回 404（不暴露资源存在性）
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
        .first()
    )
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return None