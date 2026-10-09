from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Bookmark
from schema import BookmarkCreate, BookmarkOut

app = FastAPI()

# 启动时建表
Base.metadata.create_all(bind=engine)

# 首页
@app.get("/")
def read_root():
    return {"message": "Bookmark API is running"}

# 创建书签

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