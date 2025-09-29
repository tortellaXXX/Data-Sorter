from sqlalchemy import Column, String
from .session import Base

class UserTable(Base):
    """
    Таблица для мультипользовательского режима
    session_id -> имя таблицы в Dremio
    """
    __tablename__ = "user_tables"

    session_id = Column(String, primary_key=True, index=True)
    dremio_table = Column(String, nullable=False)
