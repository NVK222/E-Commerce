from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, asc, desc, select
from db.database import get_session
from models.filter import FilterParamsUser
from models.user import User, UserReadAdmin
from utils.auth_utils import get_current_user


user_router = APIRouter()

@user_router.get('/', response_model = List[UserReadAdmin])
def get_users(filter_params : FilterParamsUser = Depends(),
              session : Session = Depends(get_session),
              user : User = Depends(get_current_user),
              ):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    
    query = select(User)

    if filter_params.name:
        query = query.where(func.lower(User.username).like(f'%{filter_params.name}%'))
    
    to_sort = getattr(User, filter_params.sort_by)
    order_values = {
        'asc' : asc,
        'desc' : desc
    }
    to_order = order_values.get(filter_params.order, asc)
    query = query.order_by(to_order(to_sort))

    query = query.offset(filter_params.offset).limit(filter_params.limit)

    return session.exec(query).all()
