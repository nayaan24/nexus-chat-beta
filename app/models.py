# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_online = Column(Integer, default=0)  # New column to track online status

    # Relationship with messages
    messages = relationship('Message', back_populates='sender')

    # Relationship with groups (many-to-many)
    groups = relationship(
        'GroupChat',
        secondary='group_memberships',
        back_populates='members',
        overlaps="group_memberships, members"
    )

# Message model
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sender_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('group_chats.id'), nullable=True)

    sender = relationship('User', back_populates='messages')
    group = relationship('GroupChat', back_populates='messages')

# Group Chat model
class GroupChat(Base):
    __tablename__ = 'group_chats'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with users (many-to-many)
    members = relationship(
        'User',
        secondary='group_memberships',
        back_populates='groups',
        overlaps="group_memberships, members"
    )

    # Relationship with messages
    messages = relationship('Message', back_populates='group')

# Group Membership model for the many-to-many relationship
class GroupMembership(Base):
    __tablename__ = 'group_memberships'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('group_chats.id'), primary_key=True)

    user = relationship(
        'User',
        backref='group_memberships',
        overlaps="groups, members"
    )
    group = relationship(
        'GroupChat',
        backref='group_memberships',
        overlaps="groups, members"
    )
