from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # deprecated automatically updates / marks old / bad hashs in our application

def hash_password(password:str): # hash password
    return pwd_context.hash(password)




def verify_passowrd(plain_password: str, hashed_password: str): # checks if plain (entered) and saved pw are the same 
    return pwd_context.verify(plain_password, hashed_password)