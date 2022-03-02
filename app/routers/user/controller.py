from flask import Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import smtplib, ssl

from .schema import UserPydantic, CreateUserPydantic
from ...database import models, connection as conn
from ...dependencies.utils import (
    QueryPaginatorMultiple,
    create_response,
    status,
    Selector,
    QueryPaginator,
    QueryPaginationParams,
    BaseCRUD
)
from ...dependencies.log import logger
from ..email.rest import emailCrud

userCrud = BaseCRUD(models.User)

async def show_user(
    request: Request,
    session: AsyncSession
):
    query_dict = request.args.to_dict()
    getParams = QueryPaginationParams(**query_dict)
    selected = Selector(
        id=models.User.id,
        email=models.Email.address,
        password=models.User.password
    )
    paginator = QueryPaginator(getParams, selected)
    query = paginator.rawQuery.join(models.Email, models.Email.id==models.User.email_id)
    if "id" in query_dict:
        query = query.where(models.User.id==query_dict["id"])
    return await paginator.execute_pagination(session, query)

async def create_user(
    request: Request,
    session: AsyncSession
):
    try:
        createUserModel = CreateUserPydantic(**request.json)

        session.add(models.Email(address=createUserModel.email))
        await session.commit()

        emailQuery = select(models.Email).where(models.Email.address==createUserModel.email)
        data = await session.execute(emailQuery)
        newEmail = data.scalars().first()

        newUser = models.User(email_id=newEmail.id, password=createUserModel.password)
        session.add(newUser)
        await session.commit()

        return create_response(status=status.success())
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))
    

async def update_user(
    request: Request,
    id: int,
    session: AsyncSession
):
    try:
        userQuery = select(models.User).where(models.User.id==id)
        user = await session.execute(userQuery)
        user = user.scalars().first()
        if user:
            if "email" in request.json:
                emailQuery = update(models.Email
                    ).where(models.Email.id==user.email_id
                    ).values(address=request.json["email"])
                await session.execute(emailQuery)
                await session.commit()
            if "password" in request.json:
                user.password = request.json["password"]
                session.add(user)
                await session.commit()
            if "email" not in request.json and "password" not in request.json:
                return create_response(status=status.data_is_not_updated())    
            return create_response(status=status.success())
        else:
            return create_response(status=status.data_is_not_exist())
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

async def remove_user(
    id: int,
    session: AsyncSession
):
    return await userCrud.delete(id, session)