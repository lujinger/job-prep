from fastapi import FastAPI
from app.routers import auth, bookmarks
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookmark API")

app.include_router(auth.router)
app.include_router(bookmarks.router)

@app.get("/")
def root():
    return {"msg": "Bookmark API is running"}


# 健康检查接口
@app.get("/health")
def health_check():
    return {"status": "ok"}