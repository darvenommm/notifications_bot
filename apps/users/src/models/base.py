from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from users.src.settings import MainSettings


class Base(DeclarativeBase):
    metadata = MetaData(schema=MainSettings().db_schema)
