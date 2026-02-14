from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.utils.logger import logger,log_exception
import uuid
from datetime import datetime


def get_friends_service(cursor, user: dict, page: int, limit: int,email=None,sort_by=None,sort_order=None):
    try:
        offset = (page - 1) * limit
        sort_by = "fr."+sort_by if sort_by else "fr.created_at"
        sort_order = sort_order if sort_order else "desc"
        email_filter = f" and u.email like '%{email}%'" if email else ""

        order_by = f" ORDER BY {sort_by} {sort_order.upper()} "

        cursor.execute(f"""
        SELECT  u.email
        FROM user u
        JOIN friends fr
          ON ( (fr.sender_id = u.id ) OR (fr.receiver_id = u.id ) )
        WHERE fr.friend_status = 'accepted' and (fr.sender_id=%s or fr.receiver_id=%s) and u.id != %s {email_filter} {order_by} LIMIT %s OFFSET %s;
        """,(user["id"],user["id"],user["id"],limit,offset))

        print(f"\n\n{cursor.statement}")
        friends = cursor.fetchall()
        return jsonable_encoder({"data": friends})

        """
        cursor.execute(f"SELECT sender_id FROM friends WHERE receiver_id=%s and friend_status=%s {email_filter} {order_by} LIMIT %s OFFSET %s ",(user["id"],"accepted",limit,offset))
        #print(f"\n\n{cursor.statement}")
        friends = cursor.fetchall()
        if not friends:
            cursor.execute(f"SELECT receiver_id FROM friends WHERE sender_id=%s and friend_status=%s  {order_by} LIMIT %s OFFSET %s ",(user["id"],"accepted",limit,offset))
            friends = cursor.fetchall()
            if not friends:
                return {f"status_code:200, message:No friends found"}
        return friends
        """
        

    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Failed to get friends for user {user['id']}")
        raise HTTPException(500, "Failed to get friends")


def friend_req(friend_id:str,user,cursor,conn):
    try:

        cursor.execute("select receiver_id from friends where sender_id=%s and receiver_id=%s and friend_status=%s",[user["id"],friend_id,"accepted"])
        #print(cursor.statement)
        result = cursor.fetchone()
        if result:
            return f"user {result} is already your friend"
        cursor.execute("select sender_id from friends where sender_id=%s and receiver_id=%s and friend_status=%s",[friend_id,user["id"],"accepted"])
        #print(cursor.statement)
        result = cursor.fetchone()
        if result:
            return f"user {result} is already your friend"

        cursor.execute("SELECT id FROM `user` where id=%s",[friend_id])
        friend_exist = cursor.fetchone()
        if not friend_exist:
            raise HTTPException(400, "user does not exist anymore")

        if friend_id == user["id"]:
            raise HTTPException(400, "Cannot send friend request to yourself")

        id = str(uuid.uuid4())

        cursor.execute("SELECT 1 FROM friends WHERE sender_id=%s and receiver_id=%s",[user["id"],friend_id])
        exists = cursor.fetchone()
        if exists:
            return "Friend request already sent! cannot send twice"
        cursor.execute(
            "INSERT INTO friends (id,sender_id, receiver_id,friend_status,updated_at) VALUES (%s, %s,%s,%s,%s)",
            (id, user["id"], friend_id, "pending",datetime.now()
))

        conn.commit()
        return { "message": f"Friend request sent to {friend_id}"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        log_exception(e,f"Failed to send friend request to {friend_id}")
        raise HTTPException(500, "Failed to send friend request")

def friend_req_pending(user,cursor):
    try:
        cursor.execute("SELECT id FROM friends WHERE receiver_id=%s and friend_status=%s",[user["id"],"pending"])
        results = cursor.fetchall()
        if not results:
            return { "message": "No pending friend requests"}
        data = [x for x in results]

        return data
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Failed to get pending friend requests for user {user['id']}")
        raise HTTPException(500, "Failed to get pending friend requests")


def accept_friend_req(friend_id,user,cursor,conn,accept: bool = False):
    try:
        if not accept:
            cursor.execute("UPDATE friends SET friend_status=%s,updated_at=%s WHERE id=%s and receiver_id=%s",[ "rejected",datetime.now(),friend_id,user["id"]])
            conn.commit()
            return { "message": "Friend request declined"}
        cursor.execute("SELECT id FROM `friends` where id=%s",[friend_id])
        user_data = cursor.fetchone()
        if not user_data:
            return "Friend does not exist anymore"

        cursor.execute("UPDATE friends SET friend_status=%s,updated_at=%s WHERE id=%s and receiver_id=%s",[ "accepted",datetime.now(),friend_id,user["id"]])
        conn.commit()
        return { "message": f"Friend request accepted to {friend_id}"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        log_exception(e,f"Failed to accept/reject friend request for user {user['id']} and friend {friend_id}")
        raise HTTPException(500, "Failed to accept/reject friend request")

def get_friends_status_service(user,cursor):
    try:
        cursor.execute("SELECT receiver_id,friend_status FROM friends WHERE sender_id=%s",(user["id"],))
        results= cursor.fetchall()
        if not results:
            results = "No friend request sent yet"
        return jsonable_encoder({"data": results})
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Failed to get friends status for user {user['id']}")
        raise HTTPException(500, "Failed to get friends status")


#get friends status
#both side friend => partial done
#sent request 2 times => done
#schema on pagination


#todo => get friends api modification in response
