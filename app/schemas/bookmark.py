from pydantic import BaseModel, ConfigDict, constr
from datetime import datetime
from typing import Optional


class BookmarkCreate(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=200)
    url: str   # 先用str，后面可改HttpUrl


class BookmarkOut(BaseModel):
    id: int
    title: str
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None