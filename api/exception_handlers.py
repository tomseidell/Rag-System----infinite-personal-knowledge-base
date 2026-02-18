from fastapi import Request, status
from fastapi.responses import JSONResponse
from shared.modules.document.exceptions import DocumentNotFoundException
from api.modules.document.exceptions import DocumentAlreadyExistsException
from shared.core.exceptions import DatabaseException, InputError, NotFoundException
from api.clients.storage.exceptions import StorageException
from api.clients.qdrant.exceptions import QdrantException

import logging

from api.modules.user.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException, WrongTokenTypeException, InvalidTokenException

logger = logging.getLogger(__name__)


def register_exception_handlers(app):

    #general
    @app.exception_handler(DatabaseException)
    async def database_error_handler(request: Request, exc: DatabaseException):
        logger.error(f"Database error: {exc.operation} - {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occured in {exc.operation}"}
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
            content={"detail": f"{exc.operation} failed"} 
        )  

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc:NotFoundException):
        logger.error(
            f"{exc.message}",
            extra={"path": request.url},
            exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message}
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
    
    @app.exception_handler(WrongTokenTypeException)
    async def wrong_token_handler(request:Request, exc:WrongTokenTypeException):
        logger.warning("Invalid token type")
        return JSONResponse(
            status_code= status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(InvalidTokenException)
    async def invalid_token_handler(request:Request, exc:InvalidTokenException):
        logger.warning("Invalid token")
        return JSONResponse(
            status_code= status.HTTP_401_UNAUTHORIZED,
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
    
    
    @app.exception_handler(QdrantException)
    async def qdrant_error_handler(request:Request, exc:QdrantException):
        logger.warning(f"Qdrant error in: {exc.operation}: {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Server error occurred while processing the document"}
        )