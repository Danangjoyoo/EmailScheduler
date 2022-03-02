from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt(password: str):
    return password_context.hash(password)

def verify(plain: str, hashed: str):
    return password_context.verify(plain, hashed)