from pydantic import BaseModel, Field
from fastapi import Query

class List_friends_filter(BaseModel):
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    email: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = "desc",




class friend_id_request(BaseModel):
    friend_id: str



