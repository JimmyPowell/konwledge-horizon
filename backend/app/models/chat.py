from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    kb_id = Column(Integer, nullable=True, index=True)
    model = Column(String(128), nullable=True)
    temperature = Column(String(16), nullable=True)
    first_message_at = Column(TIMESTAMP, nullable=True)
    last_message_at = Column(TIMESTAMP, nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    messages = relationship("Message", back_populates="conversation")


class ConversationKB(Base):
    __tablename__ = "conversation_kbs"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    kb_id = Column(Integer, nullable=False, index=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=True)
    tokens_prompt = Column(Integer, nullable=True)
    tokens_completion = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    model = Column(String(128), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    conversation = relationship("Conversation", back_populates="messages")
