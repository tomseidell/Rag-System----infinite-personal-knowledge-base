from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared.modules.document.model import Document
from shared.core.exceptions import DatabaseException
from shared.modules.document.exceptions import DocumentNotFoundException


class DocumentRepositorySync:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: int, user_id: int) -> Document:
        try:
            document = self.db.query(Document).filter(
                Document.id == document_id,
                Document.user_id == user_id,
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseException(operation="get_by_id", detail=str(e))

        if not document:
            raise DocumentNotFoundException(identifier=str(document_id))

        return document

    def finish_document(
        self, document_id: int, user_id: int, storage_path: str, chunk_count: int
    ) -> Document:
        try:
            document = self.get_by_id(document_id=document_id, user_id=user_id)
            document.status = "completed"
            document.storage_path = storage_path
            document.chunk_count = chunk_count
            self.db.commit()
            self.db.refresh(document)
            return document
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(operation="finish_document", detail=str(e))

    def mark_status_failed(
        self, document_id: int, user_id: int, error_message: str
    ) -> Document:
        try:
            document = self.get_by_id(document_id=document_id, user_id=user_id)
            document.status = "failed"
            document.error_message = error_message
            self.db.commit()
            self.db.refresh(document)
            return document
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(operation="mark_status_failed", detail=str(e))
