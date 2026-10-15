from pydantic import BaseModel, HttpUrl, constr


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)


class UserOut(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
