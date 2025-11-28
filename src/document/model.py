from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, ARRAY, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


from src.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    title: Mapped[str] = mapped_column(String)
    original_filename: Mapped[str] = mapped_column(String)
    storage_path: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    file_type: Mapped[str] = mapped_column(String)

    source_type: Mapped[str] = mapped_column(String)
    source_id: Mapped[str | None] = mapped_column(String, nullable=True)
    content_hash: Mapped[str] = mapped_column(String) # unique identifier of document

    #RAG information

    chunk_count: Mapped[int] = mapped_column(Integer)
    indexed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now) # timestamps for embeddings

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


    def __repr__(self):
        return f"<Document {self.title}>"