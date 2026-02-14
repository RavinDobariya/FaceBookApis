from fastapi import APIRouter, Depends,Query
from fastapi.security import  HTTPBearer

from app.services.user_service import get_friends_service,friend_req, friend_req_pending,accept_friend_req,get_friends_status_service
from app.database.cursor_config import get_db
from app.middleware.auth_me import get_current_user
from app.utils.response_handler import api_response
from app.schemas.user_schema import List_friends_filter


router = APIRouter(tags=["User"])

bearer_scheme = HTTPBearer()

@router.get("/friends",response_model=List_friends_filter)
def get_friends(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    email: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = "desc",
    user=Depends(get_current_user),
    db=Depends(get_db)
    ):

    cursor, conn = db
    results= get_friends_service(cursor, user, page, limit,email, sort_by,sort_order)

    return api_response(200, "Friends fetched", data=results)

@router.post("/friends-request/{friend_id}")
def friend_request(friend_id:str,user=Depends(get_current_user),db=Depends(get_db)):
    cursor, conn = db
    results = friend_req(friend_id,user,cursor,conn)
    return api_response(201, "Friend request sent",data=results)

@router.get("/friend_request/pending")
def friend_request_pending(user=Depends(get_current_user),db=Depends(get_db)):
    cursor, conn = db
    results = friend_req_pending(user,cursor)
    return api_response(200, "Friend request pending",data=results)

@router.post("/friend_request/accept/{friend_id}")
def accept_friend_request(friend_id,user=Depends(get_current_user),db=Depends(get_db),accept: bool = False):
    """
    Boolean flag to accept or reject friend request \n
    True: accept friend request \n
    False: reject friend request
    """
    cursor, conn = db
    results = accept_friend_req(friend_id,user,cursor,conn,accept)
    return api_response(201, "Friend request updated",data=results)

@router.get("/friends-status")      #todo: testing pending
def get_friend_status(user=Depends(get_current_user),db=Depends(get_db)):
    cursor, conn = db
    results = get_friends_status_service(user,cursor)
    return results