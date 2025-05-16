import os
from fastapi import Request
from jose import jwt, JWTError

SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")

async def get_current_user(request: Request):
    token = request.cookies.get('access_token')
    if token is None:
        return token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get('id')
        return user_id
    except JWTError as e:
        return None