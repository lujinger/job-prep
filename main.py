from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db
from models import Base, Bookmark
from schema import BookmarkCreate, BookmarkOut


app = FastAPI()

# 启动时建表
Base.metadata.create_all(bind=engine)


#  ---------- 首页 ----------

@app.get("/")
def read_root():
    return {"message": "Bookmark API is running"}


#  ---------- 创建 ----------

@app.post("/bookmarks", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db)):
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
def list_bookmarks(db: Session = Depends(get_db)):
    items = db.query(Bookmark).order_by(Bookmark.created_at.desc()).all()
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
