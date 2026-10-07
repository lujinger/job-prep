from fastapi import FastAPI
from database import engine
from models import Base

app = FastAPI()

# 启动时建表
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Bookmark API is running"}