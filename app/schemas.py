# app/schemas.py
from pydantic import BaseModel
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    content: str
    sender_id: int

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# GroupChat schemas
class GroupChatBase(BaseModel):
    name: str

class GroupChatCreate(GroupChatBase):
    pass

class GroupChat(GroupChatBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
