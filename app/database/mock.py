from datetime import datetime, timedelta
from . import connection as conn, models

async def mock_data():
    async with conn.session() as session:
        session.add(models.EmailAddress(id=1, address="joy.choco.banana@gmail.com"))
        session.add(models.EmailAddress(id=2, address="agus.danangjoyo.blog@gmail.com"))
        session.add(models.EmailAddress(id=3, address="tarasera.tara@gmail.com"))
        session.add(models.EmailAddress(id=4, address="rohogoho@gmail.com"))
        session.add(models.User(id=1, email_address_id=1, password="sweatyellow"))
        session.add(models.Event(id=1, owner_id=1, name="Monthly Gathering"))
        session.add(models.EmailBody(id=1, subject="Monthly Gathering Announcement", content="Hello friend!\n\nThis event gonna be fun\n\ncheers!\nJoy"))
        session.add(models.Email(id=1, sender_id=1, email_body_id=1, timestamp=datetime.now()+timedelta(minutes=1), sent=False))
        session.add(models.EmailRecipient(email_id=1, recipient_address_id=2))
        session.add(models.EmailRecipient(email_id=1, recipient_address_id=3))
        session.add(models.EmailRecipient(email_id=1, recipient_address_id=4))

        await session.commit()