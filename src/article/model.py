from sqlalchemy import Boolean, Column, Integer, String, DateTime, ARRAY, Text
from sqlalchemy.sql import func

from src.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)  # Von API
    authors = Column(ARRAY(Text), nullable=False)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False, index=True, unique=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Article {self.title}>"