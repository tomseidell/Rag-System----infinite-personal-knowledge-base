from api.modules.user.schemas import TokenResponse, UserLogin, UserRegistration, UserResponse
from api.modules.user.utils import create_access_token, create_refresh_token, hash_password, verify_password, decode_refresh_token
from api.modules.user.repository import UserRepository
from api.modules.user.exceptions import UserNotFoundException, InvalidTokenException, UserAlreadyExistsException, InvalidCredentialsException



class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: UserRegistration) -> UserResponse: 
        existing_user = await self.user_repository.get_user_by_mail(user.email)
        if existing_user:
            raise UserAlreadyExistsException(email=user.email)

        hashed_password = hash_password(user.password)
        user = await self.user_repository.create_user(full_name=user.fullname, email=user.email, hashed_password=hashed_password)
        return UserResponse.model_validate(user)


    async def login_user(self, user_login:UserLogin) -> TokenResponse:
        user = await self.user_repository.get_user_by_mail(user_login.email)

        if not user:
            raise UserNotFoundException(identifier=user_login.email)

        is_valid = verify_password(user_login.password, user.hashed_password)

        if not is_valid:
            raise InvalidCredentialsException(email=user_login.email)
        
        await self.user_repository.update_last_login(user.id)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        await self.user_repository.update_refresh_token(user.id, refresh_token)
        
        return TokenResponse(
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type="bearer", 
            expires_in=1800
        )


    async def handle_refresh(self, refresh_token:str) ->TokenResponse:
        user_id = decode_refresh_token(refresh_token)
        db_user = await self.user_repository.get_user_by_id(id=user_id)

        if not db_user:
            raise UserNotFoundException(identifier=user_id)

        if db_user.refresh_token != refresh_token:
            raise InvalidTokenException()
        
        new_access_token = create_access_token(user_id)

        new_refresh_token = create_refresh_token(user_id)

        await self.user_repository.update_refresh_token(user_id, refresh_token)

        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, expires_in=1800) 
