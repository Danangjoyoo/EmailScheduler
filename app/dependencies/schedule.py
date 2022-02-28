import asyncio, time
from typing import List
from worker import worker, enableKeyboardInterrupt
from datetime import datetime
from sqlalchemy import select

from .log import logger
from ..database import models, connection as conn
from ..routers.email.controller import set_email_sent

class Scheduler():
    def __init__(self, interval: float):
        """
        Email Scheduler Class

        :params interval: interval time for checking the email in the database constantly (seconds)
        """
        self._interval = float(interval)
        self.worker_object = None
        self._run = False

    async def check_scheduled_email(self) -> list:
        try:
            async with conn.session() as session:
                query = select(models.Email
                    ).where(models.Email.timestamp <= datetime.now()
                    ).where(models.Email.sent==False)
                datas = await session.execute(query)
                datas = datas.scalars().all()
                return datas
        except:
            return []

    @worker("Email Sender")
    def send_email(self, data):
        try:
            logger.info(f"Sending data.. data={str(data)}")
            # asyncio.run()
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
                datas: List[models.Email] = asyncio.run(self.check_scheduled_email())
                for data in datas:
                    if self.send_email(data):
                        asyncio.run(set_email_sent(data.event_id))
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