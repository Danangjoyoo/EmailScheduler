import asyncio, time, smtplib, ssl
from typing import List
from worker import worker, enableKeyboardInterrupt
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .log import logger
from ..database import models, connection as conn
from ..dependencies.utils import create_response, status, Selector

class Scheduler():
    def __init__(self, interval: float):
        """
        Email Scheduler Class

        :params interval: interval time for checking the email in the database constantly (seconds)
        """
        self._interval = float(interval)
        self.worker_object = None
        self._run = False
        self._queue = []
        self._queue_sender_active = False

    @worker("Queue Sender", on_abort=lambda: logger.info("Scheduler Stopped.."))
    def queue_sender(self):
        while self._queue:
            if not self._queue_sender_active:
                self._queue_sender_active = True
            poped_email = self._queue.pop()
            total = len(poped_email["participant"])
            success = 0
            logger.info(f"Processing Queue Start.. total:{total}")
            for participant in poped_email["participant"]:
                send_success = self.send_email(poped_email, participant["address"])
                success += int(send_success)
            logger.info(f"Processing Queue End.. succeed:{success} failed:{total-success}")
        self._queue_sender_active = False

    async def set_email_sent(self, event_id: int):
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

    async def check_scheduled_email(self):
        try:
            datas = []
            async with conn.session() as sess:
                timestamp_now_in_utc_plus_8 = datetime.utcnow()+timedelta(hours=8)
                # timestamp_now_in_utc_plus_8 = datetime.now()
                emailQuery = select(models.Email
                    ).where(models.Email.timestamp<=timestamp_now_in_utc_plus_8
                    ).where(models.Email.sent==False)
                emails = await sess.execute(emailQuery)
                emails = emails.scalars().all()
                if not emails:
                    return []
                for email in emails:
                    wrapped = await self.wrap_email(email, sess)
                    datas.append(wrapped)
            return datas
        except Exception as e:
            logger.error(e)
            return []

    async def wrap_email(self, email: models.Email, session: AsyncSession):
        selected = Selector(
            id=models.Email.id,
            event_id=models.Event.id,
            event_name=models.Event.name,
            sender_email=models.EmailAddress.address,
            sender_password=models.User.password,
            subject=models.Email.subject,
            content=models.Email.content
        )
        query = selected.query\
            .join(models.Event, models.Event.id==models.Email.event_id)\
            .join(models.User, models.User.id==models.Email.sender_id)\
            .join(models.EmailAddress, models.EmailAddress.id==models.User.email_address_id)\
            .where(models.Email.id==email.id)        
        email_data = await selected.execute(session, query)
        email_data = email_data[0]
        participant_data = await self.wrap_participant(email.event_id, session)
        email_data["participant"] = participant_data
        await self.set_email_sent(email.event_id)
        return email_data

    async def wrap_participant(self, event_id, session):
        selected = Selector(
            participant_id=models.EventParticipant.id,
            address=models.EmailAddress.address
            )
        query = selected.query\
            .join(models.EmailAddress, models.EmailAddress.id==models.EventParticipant.address_id)\
            .where(models.EventParticipant.event_id==event_id)
        data = await selected.execute(session, query)
        return data

    def send_email(self, data, participant):
        try:
            logger.info(f"Sending data.. sender={data['sender_email']} receiver={participant}")
            port = 465  # SSL
            smtp_server = "smtp.gmail.com"
            message = f"Subject: {data['subject']}\n{data['content']}"
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                try:
                    server.login(data["sender_email"], data["sender_password"])
                except smtplib.SMTPAuthenticationError as e:
                    if e.smtp_code == 535:
                        err = """\
                        Possible Authentication Error:\
                        \n- Username and Password are not match\
                        \n- Your 2-Step Verification is enabled\
                        \n- Your Less-Secure-Authentication is disabled (if gmail, you can visit this https://www.google.com/settings/security/lesssecureapps)\
                        """
                        logger.error(err)
                        raise BaseException(err)
                    logger.error(e)
                    raise e
                except Exception as e:
                    logger.error(e)
                    raise e
                server.sendmail(data["sender_email"], participant, message)
                return True
        except Exception as e:
            logger.error(e)
            return False

    @worker("Email Scheduler", on_abort=lambda: logger.info("Scheduler Stopped.."))
    def create_scheduler(self, delay):
        time.sleep(delay)
        logger.info("Scheduler Started..")
        while self._run:
            try:                
                logger.info("Checking Schedule..")
                emails = asyncio.run(self.check_scheduled_email())
                self._queue.extend(emails)
                if not self._queue_sender_active:
                    self.queue_sender()
                # for email in emails:
                #     for participant in email["participant"]:
                #         self.send_email(email, participant["address"])
                time.sleep(self._interval)
            except Exception as e:
                logger.error(e)
        logger.info("Scheduler Stopped..")

    def start(self, delay: float = 2):
        """
        :params delay: delay time before scheduler start checking (seconds)
        """        
        enableKeyboardInterrupt()
        self._run = True
        self.worker_object = self.create_scheduler(delay=delay)
        return self.worker_object
    
    def stop(self):
        self._run = False
