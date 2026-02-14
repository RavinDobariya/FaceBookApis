from fastapi.responses import JSONResponse

#api_response(status_code,message,data,error)
#return api_response(200, "Companies fetched", data=str/dict, error="IndexError")

def api_response(status_code: int = 200,message: str = "success",data=None,error: str = None):
    payload ={
        "message": message,
        "data": data,
        "error": error
    }
    
    return JSONResponse(status_code=status_code,content=payload)