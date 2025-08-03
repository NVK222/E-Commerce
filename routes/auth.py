from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.database import get_session
from models.tokens import Token
from models.user import User, UserCreate, UserRead
from utils.auth_utils import create_access_token, get_current_user, get_password_hash, verify_password


auth_router = APIRouter()

@auth_router.post('/register', response_model = UserRead)
def register(user : UserCreate, session :  Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == user.email)).first()
    if exists:
        raise HTTPException(400, 'Email already exists.')
    hashed_pw = get_password_hash(user.password)
    db_user = User(username = user.username, email = user.email, password = hashed_pw)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@auth_router.post('/login', response_model = Token)
def login(user : UserCreate, session : Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(400, 'Invalid credentials')
    token = create_access_token({
        'sub' : str(db_user.id)
    })
    return {
        'access_token' : token,
        'token_type' : 'bearer',
        'user' : UserRead.model_validate(db_user.model_dump())
    }

@auth_router.put('/', response_model = dict)
def update(username : str | None = None, email : str | None = None, password : str | None = None, user : User = Depends(get_current_user), session : Session = Depends(get_session)):
    if not user:
        raise HTTPException(400, 'Invalid credentials')
    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.password = get_password_hash(password)
    session.commit()
    return {
        'message' : 'Details updated successfully'
    }

@auth_router.delete('/', response_model = dict)
def delete(user : User = Depends(get_current_user), session : Session = Depends(get_session)):
    if not user:
        raise HTTPException(400, 'Invalid credentials')
    session.delete(user)
    session.commit()
    return {
        'message' : 'Profile has been successfully deleted'
    }

@auth_router.put('/{id}', response_model = dict)
def admin_update(id : int, username : str, user : User = Depends(get_current_user), session : Session = Depends(get_session)):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    user_ = session.get(User, id)
    if not user_:
        raise HTTPException(404, 'User not found')
    user_.username = username
    session.commit()
    return {
        'message' : "User's username has been changed successfully"
    }


@auth_router.delete('/{id}', response_model = dict)
def admin_delete(id : int, user : User = Depends(get_current_user), session : Session = Depends(get_session)):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    user_ = session.get(User, id)
    if not user_:
        raise HTTPException(404, 'User not found')
    session.delete(user_)
    session.commit()
    return {
        'message' : 'User has been deleted'
    }