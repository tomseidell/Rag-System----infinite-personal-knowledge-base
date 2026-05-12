import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError
from worker.document.document_repository import DocumentRepositorySync
from shared.core.exceptions import DatabaseException


@pytest.fixture(scope="function")
def repository():
    return DocumentRepositorySync(db=MagicMock())


def _mock_document():
    return MagicMock(id=1, user_id=2, status="pending")



def test_finish_document_sets_status_completed(repository):
    doc = _mock_document()
    repository.db.query.return_value.filter.return_value.first.return_value = doc

    repository.finish_document(document_id=1, user_id=2, storage_path="s3/path", chunk_count=5)

    assert doc.status == "completed"
    assert doc.storage_path == "s3/path"
    assert doc.chunk_count == 5
    repository.db.commit.assert_called_once()

def test_finish_document_raises_database_exception(repository):
    doc = _mock_document()
    repository.db.query.return_value.filter.return_value.first.return_value = doc

    # mock db exception
    repository.db.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseException, match="finish_document"):
        repository.finish_document(document_id=1, user_id=2, storage_path="s3/path", chunk_count=5)

    repository.db.rollback.assert_called_once()



def test_mark_status_failed_sets_status(repository):
    doc = _mock_document()
    repository.db.query.return_value.filter.return_value.first.return_value = doc

    repository.mark_status_failed(document_id=1, user_id=2, error_message="something went wrong")

    assert doc.status == "failed"
    assert doc.error_message == "something went wrong"
    repository.db.commit.assert_called_once()

def test_mark_status_failed_raises_database_exception(repository):
    doc = _mock_document()
    repository.db.query.return_value.filter.return_value.first.return_value = doc

    # mock db exception
    repository.db.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseException, match="mark_status_failed"):
        repository.mark_status_failed(document_id=1, user_id=2, error_message="error")

    repository.db.rollback.assert_called_once()
