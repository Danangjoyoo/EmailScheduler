from sqlalchemy import select, update
import smtplib, ssl

from .schema import EmailPydantic
from ...database import models, connection as conn
from ...dependencies.utils import create_response, status, extract_and_count_object

async def show_email():
    try:
        async with conn.session() as session:
            data = await session.execute(select(models.Email))
            data = data.scalars().all()
            total, data = extract_and_count_object(data)
            return create_response(
                data=data,
                meta={"total":total},
                status=status.success())
    except Exception as e:
        return create_response(status=status.error(e))

async def create_scheduled_email(email: EmailPydantic):
    try:
        async with conn.session() as session:
            session.add(
                models.Email(**email.dict())
                )
            await session.commit()
            return create_response(status=status.success())
    except Exception as e:
        return create_response(status=status.error(e))

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