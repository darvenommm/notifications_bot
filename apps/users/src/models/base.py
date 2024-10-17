from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from users.src.settings.main import main_settings


class Base(DeclarativeBase):
    metadata = MetaData(schema=main_settings.db_schema)
