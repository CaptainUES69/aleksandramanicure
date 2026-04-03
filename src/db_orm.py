from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .utility import FormData
from .conf import CustomLogger, Logger


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    ID: Mapped[int] = mapped_column(primary_key=True)
    Email: Mapped[str] = mapped_column(nullable=False)
    Name: Mapped[str] = mapped_column(nullable=False)
    Course: Mapped[str] = mapped_column(nullable=False)
    Status: Mapped[str] = mapped_column(nullable=True)


load_dotenv(override=True)

engine = create_engine(getenv("DBROOT"), echo=False)

Base.metadata.create_all(engine)
session_factory = sessionmaker(engine)


class TableManager:
    logger: Logger = CustomLogger("db")._logger

    def get_user(self, email: str) -> Users | None:
        with session_factory() as session:
            user = session.query(Users).filter(Users.Email == email).first()
            if not user:
                return None

            self.logger.info(f"Get user with ID: {user.ID}, Email: {user.Email}")
            return user

    def get_users(self, email: str) -> list[Users] | None:
        with session_factory() as session:
            users = session.query(Users).filter(Users.Email == email).all()
            if not users:
                return None

            self.logger.info(f"Get users with Email: {email}")
            return users

    def create_user(self, data: FormData) -> None:
        with session_factory() as session:
            user = Users(
                Email=data.Email, Name=data.Name, Course=data.payment.products[0].name
            )
            session.add(user)
            session.commit()
            self.logger.info("User succesfully created")

    def change_status(self, email: str, status: str) -> None:
        with session_factory() as session:
            user = session.query(Users).filter(Users.Email == email).first()
            user.Status = status
            session.refresh(user)
            session.commit()
            self.logger.info("Status changed succesfully")
