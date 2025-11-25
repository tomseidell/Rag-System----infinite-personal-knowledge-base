from fastapi import Request, status
from fastapi.responses import JSONResponse
from document.exceptions import DocumentAlreadyExistsException, DocumentNotFoundException
from src.core.exceptions import DatabaseException, InputError
from src.storage.exceptions import StorageException

import logging

from user.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException

logger = logging.getLogger(__name__)


def register_exception_handlers(app):

    #general
    @app.exception_handler(DatabaseException)
    async def database_error_handler(request: Request, exc: DatabaseException):
        logger.error(f"Database error: {exc.operation} - {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occured"}
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
            content={"detail": "An error occured"}
        )

    @app.exception_handler(InputError)
    async def input_exception_handler(request: Request, exc: InputError):
        logger.error(f"Invalid input in {exc.operation}: {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": exc.detail,
                "operation": exc.operation  
            }
        )

    @app.exception_handler(StorageException)
    async def bucket_exception_handler(request: Request, exc:StorageException):
        logger.error(
            f"Bucket error occured in: {exc.operation}",
            extra={"path": request.url},
            exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "file upload failed"} 
        )  


    
    #user
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
    

    #document
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
    
    