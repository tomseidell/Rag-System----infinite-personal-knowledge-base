class UserException(Exception):
    pass

class UserNotFoundException(UserException):
    def __init__(self, identifier:str):
        self.identifier = identifier
        self.message = f"User not found: {self.identifier}"
        super().__init__(self.message) # wird weitergeleited zu Exception init

class UserAlreadyExistsException(UserException):
    def __init__(self, email:str):
        self.email = email
        self.message = f"User already exists: {self.email}"
        super().__init__(self.message)


class InvalidCredentialsException(UserException):
    def __init__(self, email:str):
        self.email = email
        self.message = f"Password for user {self.email} is wrong"
        super().__init__(self.message)

