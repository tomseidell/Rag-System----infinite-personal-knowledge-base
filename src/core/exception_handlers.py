from fastapi import Request, status
from fastapi.responses import JSONResponse
from document.exceptions import DocumentAlreadyExistsException, DocumentNotFoundException
from src.core.exceptions import DatabaseException

import logging

from user.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException

logger = logging.getLogger(__name__)


def register_exception_handlers(app):
    
    @app.exception_handler(DocumentNotFoundException)
    async def document_not_found_handler(request: Request, exc: DocumentNotFoundException):
        logger.warning(f"Document not found: {exc.identifier}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(DocumentAlreadyExistsException)
    async def document_exists_handler(request: Request, exc: DocumentAlreadyExistsException):
        logger.warning(f"Document already exists: {exc.identifier}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException):
        logger.warning(f"User not found: {exc.identifier}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(UserAlreadyExistsException)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsException):
        logger.warning(f"User already exists: {exc.email}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
        logger.warning("Invalid credentials attempt")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(DatabaseException)
    async def database_error_handler(request: Request, exc: DatabaseException):
        logger.error(f"Database error: {exc.operation} - {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ein Datenbankfehler ist aufgetreten"}
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ein unerwarteter Fehler ist aufgetreten"}
        )
