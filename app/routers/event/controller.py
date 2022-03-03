from flask import Request
from sqlalchemy import delete, select, update
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

crud = BaseCRUD(models.Event)
participantCrud = BaseCRUD(models.EventParticipant)

async def show_event(
    request: Request,
    session: AsyncSession
):
    getParams = QueryPaginationParams(**request.args.to_dict())
    selected = Selector(
        event_name=models.Event.name,
        owner=models.EmailAddress.address
    )
    paginator = QueryPaginator(getParams, selected)
    query = paginator.rawQuery\
        .join(models.User, models.User.id==models.Event.owner_id)\
        .join(models.EmailAddress, models.EmailAddress.id==models.User.email_address_id)
    return await paginator.execute_pagination(session, query)

async def create_event(
    request: Request,
    session: AsyncSession
):
    event = schema.EventPydantic(**request.json)
    return await crud.create(event, session)

async def update_event(
    request: Request,
    id: int,
    session: AsyncSession
):
    event = schema.EditEventPydantic(**request.json)
    return await crud.update(event, id, session)

async def remove_event(
    id: int,
    session: AsyncSession
):
    await session.execute(
        delete(models.EventParticipant).where(models.EventParticipant.event_id==id)
    )
    return await crud.delete(id, session)

async def show_participant(
    request: Request,
    event_id: int,
    session: AsyncSession
):
    query_dict = request.args.to_dict()
    getParams = QueryPaginationParams(**query_dict)
    selected = Selector(id=models.EventParticipant.id, address=models.EmailAddress.address)
    paginator = QueryPaginator(getParams, selected)
    query = paginator.rawQuery\
        .join(models.EmailAddress, models.EmailAddress.id==models.EventParticipant.address_id)\
        .join(models.Event, models.Event.id==models.EventParticipant.event_id)\
        .where(models.Event.id==event_id)
    return await paginator.execute_pagination(session, query)   

async def set_participant(
    request: Request,
    event_id: int,
    session: AsyncSession
):
    address = request.json["address"]

    emailAddressObj = await session.execute(
        select(models.EmailAddress).where(models.EmailAddress.address==address)
    )
    emailAddressObj = emailAddressObj.scalars().first()

    if not emailAddressObj:
        session.add(models.EmailAddress(address=address))
        await session.commit()
        emailAddressObj = await session.execute(
            select(models.EmailAddress).where(models.EmailAddress.address==address)
        )
        emailAddressObj = emailAddressObj.scalars().first()
    
    participant = await session.execute(
        select(models.EventParticipant
        ).where(models.EventParticipant.event_id==event_id
        ).where(models.EventParticipant.address_id==emailAddressObj.id)
    )
    participant = participant.scalars().first()

    if participant:
        return create_response(status=status.data_is_not_updated())
    
    session.add(models.EventParticipant(event_id=event_id, address_id=emailAddressObj.id))
    await session.commit()
    return create_response(status=status.success())

async def remove_participant(
    participant_id: int,
    session: AsyncSession
):
    return await participantCrud.delete(participant_id, session)