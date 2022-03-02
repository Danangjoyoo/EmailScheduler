from flask import Request
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
import smtplib, ssl

from . import schema
from ...database import models, connection as conn
from ...dependencies.utils import (
    Selector,
    create_response,
    status,
    QueryPaginator,
    QueryPaginationParams,
    BaseCRUD
)
from ...dependencies.log import logger

emailCrud = BaseCRUD(models.Email)

async def show_email(
    request: Request,
    session: AsyncSession
):
    query_dict = request.args.to_dict()
    getParams = QueryPaginationParams(**query_dict)
    selected = Selector(
        id=models.Email.id,
        email_sender=models.EmailAddress.address,
        email_subject=models.EmailBody.subject,
        email_content=models.EmailBody.content,
        timestamp=models.Email.timestamp,
        sent=models.Email.sent
    )
    paginator = QueryPaginator(getParams, selected)
    query = paginator.rawQuery
    query = query.join(models.EmailAddress, models.EmailAddress.id==models.Email.sender_id)
    query = query.join(models.EmailBody, models.EmailBody.id==models.Email.email_body_id)
    return await paginator.execute_pagination(session, query)

async def create_email(
    request: Request,
    session: AsyncSession
):
    email = schema.EmailPydantic(**request.json)
    return await emailCrud.create(email, session)

async def update_email(
    request: Request,
    id: int,
    session: AsyncSession
):
    email = schema.EmailPydantic(**request.json)
    return await emailCrud.update(email, id, session)

async def remove_email(
    id: int,
    session: AsyncSession
):
    return await emailCrud.delete(id, session)


addressCrud = BaseCRUD(models.EmailAddress)

async def show_address(
    request: Request,
    session: AsyncSession
):
    query_dict = request.args.to_dict()
    getParams = QueryPaginationParams(**query_dict)
    if "id" in query_dict:
        wc = addressCrud.where(models.Email.id==query_dict["id"])
        return await addressCrud.read(getParams, session, wc)
    else:
        return await addressCrud.read(getParams, session)

async def create_address(
    request: Request,
    session: AsyncSession
):
    address = schema.EmailAddressPydantic(**request.json)
    return await addressCrud.create(address, session)

async def update_address(
    request: Request,
    id: int,
    session: AsyncSession
):
    address = schema.EmailAddressPydantic(**request.json)
    return await addressCrud.update(address, id, session)

async def remove_address(
    id: int,
    session: AsyncSession
):
    return await addressCrud.delete(id, session)




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