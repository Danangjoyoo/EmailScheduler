from flask import Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import smtplib, ssl

from .schema import EmailPydantic, ScheduledEmailPydantic
from ...database import models, connection as conn
from ...dependencies.utils import (
    create_response,
    status,
    QueryPaginator,
    QueryPaginationParams,
    BaseCRUD
)
from ...dependencies.log import logger

crud = BaseCRUD(models.Email)

async def show_email(
    request: Request,
    session: AsyncSession
):
    getParams = QueryPaginationParams(**request.args.to_dict())
    return await crud.read(getParams, session)

async def create_email(
    request: Request,
    session: AsyncSession
):
    email = EmailPydantic(**request.json)
    return await crud.create(email, session)

async def update_email(
    request: Request,
    id: int,
    session: AsyncSession
):
    email = EmailPydantic(**request.json)
    return await crud.update(email, id, session)

async def remove_email(
    id: int,
    session: AsyncSession
):
    return await crud.delete(id, session)

async def create_scheduled_email(
        request: Request,
        session: AsyncSession
    ):
    scheduledEmail = ScheduledEmailPydantic(**request.json)
    session.add(
        models.Email(**scheduledEmail.dict())
        )
    await session.commit()
    return create_response(status=status.success())

async def set_email_sent(event_id: int):
    try:
        async with conn.session() as session:
            query = update(models.Email
                ).where(models.Email.event_id==event_id
                ).values(sent=True)
            await session.execute(query)
            await session.commit()
            return create_response(status=status.success())
    except Exception as e:
        return create_response(status=status.error(e))

async def send_email(email: models.Email):
    port = 587
    smtp_server = "smtp.gmail.com"