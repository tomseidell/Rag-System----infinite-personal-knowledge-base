import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from shared.database import Base
import shared.modules.user.model  # noqa: F401
import shared.modules.document.model  # noqa: F401
import shared.modules.chunk.model  # noqa: F401

from api.modules.user.repository import UserRepository
from api.modules.document.repository import DocumentRepository
from api.modules.document.schemas import DocumentCreate



# test database in ram
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user_and_fetch_by_email(db):
    repo = UserRepository(db=db)

    await repo.create_user(full_name="Tom", email="tom@test.com", hashed_password="hash")
    user = await repo.get_user_by_mail("tom@test.com")

    # user should be saved properly and should be accessible by mail
    assert user is not None
    assert user.email == "tom@test.com"
    assert user.full_name == "Tom"


@pytest.mark.asyncio
async def test_get_user_by_mail_returns_none_for_unknown(db):
    repo = UserRepository(db=db)

    user = await repo.get_user_by_mail("unknown@test.com")

    assert user is None


@pytest.mark.asyncio
async def test_create_document_and_fetch(db):
    user_repo = UserRepository(db=db)
    doc_repo = DocumentRepository(db=db)

    user = await user_repo.create_user(full_name="Tom", email="tom@test.com", hashed_password="hash")

    doc_data = DocumentCreate(
        user_id=user.id,
        title="My Doc",
        original_filename="file.pdf",
        source_type="pdf",
        content_hash="abc123",
        file_size=1024,
        file_type="application/pdf",
    )
    created = await doc_repo.create_document(doc_data)
    fetched = await doc_repo.get_document(user_id=user.id, document_id=created.id)

    assert fetched is not None
    assert fetched.title == "My Doc"
    assert fetched.content_hash == "abc123"
