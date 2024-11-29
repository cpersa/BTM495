from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from renova.context import Context
from renova.models.users import User


class LoginContext(Context):
    password_hasher = PasswordHasher()

    def login[T: User](self, user_type: type[T], email: EmailStr, password) -> T:
        try:
            user = self.session.exec(
                select(user_type).where(user_type.email_address == email)
            ).one()
        except NoResultFound as e:
            raise HTTPException(401, f"{user_type.__name__} {email} not found") from e

        if not self.verify(user, password):
            raise HTTPException(401, "wrong password")

        return user

    def hash(self, password: str) -> str:
        return self.password_hasher.hash(password)

    def verify(self, user: User, password: str) -> bool:
        try:
            self.password_hasher.verify(user.hash, password)
        except InvalidHashError:
            return False

        if self.password_hasher.check_needs_rehash(user.hash):
            user.hash = self.hash(password)
            self.session.add(user)
            self.session.commit()

        return True
