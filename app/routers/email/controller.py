from datetime import datetime, timedelta
import smtplib, ssl
from flask import Request, session
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

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
addressCrud = BaseCRUD(models.EmailAddress)

async def show_email(
    request: Request,
    session: AsyncSession
):
    query_dict = request.args.to_dict()
    getParams = QueryPaginationParams(**query_dict)
    selected = Selector(
        id=models.Email.id,
        event_name=models.Event.name,
        email_sender=models.EmailAddress.address,
        email_subject=models.Email.subject,
        email_content=models.Email.content,
        timestamp=models.Email.timestamp,
        sent=models.Email.sent
    )
    paginator = QueryPaginator(getParams, selected)
    query = paginator.rawQuery\
        .join(models.EmailAddress, models.EmailAddress.id==models.Email.sender_id)\
        .join(models.Event, models.Event.id==models.Email.event_id)
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
    email = schema.EditEmailPydantic(**request.json)
    return await emailCrud.update(email, id, session)

async def remove_email(
    id: int,
    session: AsyncSession
):
    return await emailCrud.delete(id, session)

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


########## main function ########## main function ########## main function ########## main function 
### main function ########## main function ########## main function ########## main function 
########## main function ########## main function ########## main function ########## main function 


## saat ini hanya bisa kirim lewat user-1 (joy.choco.banana@gmail.com)
## ideally bisa menggunakan login untuk define user mana yang request
async def create_scheduled_email(
    request: Request,
    session: AsyncSession
):
    event_id = request.json["event_id"]
    subject = request.json["email_subject"]
    content = request.json["email_content"]
    timestamp = request.json["timestamp"]
    email = schema.EmailPydantic(
        sender_id=1,
        event_id=event_id,
        subject=subject,
        content=content,
        timestamp=timestamp
    )
    return await emailCrud.create(email, session)