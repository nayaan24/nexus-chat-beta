from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(content=message.content, sender_id=message.sender_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
