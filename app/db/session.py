from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Для SQLite
DATABASE_URL = "sqlite:///./db.sqlite"
# Для PostgreSQL (пример)
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # нужно для SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
