from fastapi import FastAPI, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from database import engine, get_db
from models import Base, Bookmark, User
from schema import BookmarkCreate, BookmarkOut, BookmarkUpdate, UserCreate, UserOut, Token
from auth import (
    get_password_hash, create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, verify_password
)


app = FastAPI()

# 启动时建表
Base.metadata.create_all(bind=engine)


#  ---------- 首页 ----------

@app.get("/")
def read_root():
    return {"message": "Bookmark API is running"}


# --- 用户注册 ---
@app.post("/register", response_model=UserOut, tags=["auth"])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed_pw = get_password_hash(user_in.password)
    user = User(username=user_in.username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- 用户登录 ---
@app.post("/login", response_model=Token, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


#  ---------- 创建，加上认证 ----------

@app.post("/bookmarks", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED, tags=["bookmarks"])
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

@app.get("/bookmarks", response_model=List[BookmarkOut], tags=["bookmarks"])
def list_bookmarks(
    skip: int = Query(0, ge=0, description="跳过前N条"),
    limit: int = Query(10, ge=1, le=100, description="返回最多N条"),
    q: str = Query(None, min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db)
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
            id=item.id,
            title=item.title,
            url=item.url,
            created_at=item.created_at.isoformat() if item.created_at else "",
        )
        for item in items
    ]


# ---------- 单条查询 ----------

@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkOut, tags=["bookmarks"])
def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
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

@app.put("/bookmarks/{bookmark_id}", response_model=BookmarkOut, tags=["bookmarks"])
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

@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["bookmarks"])
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
