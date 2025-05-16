import os
from datetime import timedelta, datetime
from jose import jwt

SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")

async def create_access_token(username: str, user_id: int):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + timedelta(hours=1)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
