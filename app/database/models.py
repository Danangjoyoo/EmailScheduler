from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

Base = declarative_base()

class EmailAddress(Base):
    __tablename__ = "email_address"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    address = Column(String(100), nullable=False, unique=True)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email_address_id = Column(Integer, ForeignKey("email_address.id"), unique=True)
    email_address = relationship("EmailAddress")
    password = Column(String(100), nullable=False)

class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User")
    name = Column(String(100), nullable=False)

class EmailBody(Base):
    __tablename__ = "email_body"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    subject = Column(String(300), nullable=True)
    content = Column(Text, nullable=False)

class Email(Base):
    __tablename__ = "email"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.id"))
    sender = relationship("User")
    email_body_id = Column(Integer, ForeignKey("email_body.id"))
    email_body = relationship("EmailBody")
    timestamp = Column(DateTime, nullable=False)
    sent = Column(Boolean, nullable=False, default=False)

class EmailRecipient(Base):
    __tablename__ = "email_recipient"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email_id = Column(Integer, ForeignKey("email.id"))
    email = relationship("Email")
    recipient_address_id = Column(Integer, ForeignKey("email_address.id"))
    recipient = relationship("EmailAddress")