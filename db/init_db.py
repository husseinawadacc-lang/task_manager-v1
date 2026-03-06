
#Create DATABASE Tables
from db.base import Base
from db.session import engine

# import models so they register in metadate
from db.models import user
from db .models import task
from db.models import refresh_token
from db.models import password_reset
def init_db():
    """
    Initialize database tables.
    create all tables
    when DATABASE_URL is configured and database is running.
    """
   
    Base.metadata.create_all(bind=engine)