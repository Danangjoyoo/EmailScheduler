from flask import Blueprint, request, session

from .controller import (
    show_user,
    create_user, 
    update_user,
    remove_user
)
from .schema import UserPydantic
from ...dependencies.utils import create_response, status, QueryPaginationParams
from ...dependencies.log import logger
from ...database import connection as conn

router = Blueprint(
    name="user", 
    import_name=__name__,
    url_prefix="/user",
    template_folder="/routers/user",
    )

@router.get("")
async def get_user():
    try:
        async with conn.session() as session:
            return await show_user(request, session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))
    

@router.post("")
async def post_user():
    try:
        async with conn.session() as session:
            return await create_user(request, session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.put("/<id>")
async def put_user(id: int):
    try:
        async with conn.session() as session:
            return await update_user(request, id, session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.delete("/<id>")
async def delete_user(id: int):
    try:
        async with conn.session() as session:
            return await remove_user(id, session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))