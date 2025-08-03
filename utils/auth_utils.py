from datetime import timedelta, datetime, timezone
from os import getenv
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from sqlmodel import Session

from db.database import get_session
from models.user import User

load_dotenv()
SECRET_KEY = getenv("AUTH_SECRET_KEY")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes = ['bcrypt'],deprecated = 'auto')
oauth2_scheme = HTTPBearer()

def create_access_token(data : dict, expire_delta : timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = 15)
    to_encode.update({
        'exp' : expire
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def verify_password(plain_pw : str, hashed_pw : str):
    return pwd_context.verify(plain_pw, hashed_pw)

def get_password_hash(pw : str):
    return pwd_context.hash(pw)

def decode_access_token(token : str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(credentials : HTTPAuthorizationCredentials = Depends(oauth2_scheme), session : Session = Depends(get_session)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(401, 'Invalid or expired token')
    user = session.get(User, int(payload['sub']))
    return user