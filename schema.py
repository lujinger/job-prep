from pydantic import BaseModel, HttpUrl, constr

class BookmarkCreate(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=200)
    url: str   # 先用str，后面可改HttpUrl

class BookmarkOut(BaseModel):
    id: int
    title: str
    url: str
    # created_at 如果是DateTime，可写 datetime；这里用iso字符串更省事
    created_at: str

    model_config = {
        "from_attributes": True   # Pydantic v2：允许从ORM对象读属性
    }