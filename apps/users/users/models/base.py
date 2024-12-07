from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from libs.settings.database import DatabaseSettings


class Base(DeclarativeBase):
    metadata = MetaData(schema=DatabaseSettings().db_schema)
