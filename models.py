from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)