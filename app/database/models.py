from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = "email"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    address = Column(String(100), nullable=False, unique=True)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email_id = Column(Integer, ForeignKey("email.id"), unique=True)
    email = relationship("Email")
    password = Column(String(100), nullable=False)

class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User")
    email_subject = Column(String(300), nullable=True)
    email_content = Column(String(1000), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    done = Column(Boolean, nullable=False, default=False)

class EmailHasEvent(Base):
    __tablename__ = "email_has_event"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("email.id"))
    email = relationship("Email")
    event_id = Column(Integer, ForeignKey("event.id"))
    event = relationship("Event")