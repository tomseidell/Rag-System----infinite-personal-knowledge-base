class UserException(Exception):
    pass

class UserNotFoundException(UserException):
    def __init__(self, identifier:str | int):
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
        self.message = f"Invalid Email or Password"
        super().__init__(self.message)


class InvalidTokenException(Exception):
    def __init__(self, detail: str = "Invalid token"):
        self.message = detail

class WrongTokenTypeException(Exception):
    def __init__(self):
        self.message = "Wrong token type"
