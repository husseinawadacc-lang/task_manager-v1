from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_settings

def get_engine():
    settings = get_settings()
    #Enigine manages connection pool

    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True, # يتحقق من الاتصال قبل الاستخدام
        future=True,# SQLAlchemy 2.x style
    )


engine = get_engine()
# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,# no change save automatic, must session.commit
    autocommit=False,# no commit or rollback automatic
    future=True,
)


