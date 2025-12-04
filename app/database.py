import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


#############################
#       DB CONNECTION       #
#############################
# temp way to store db password
load_dotenv()
CONN_URL = os.getenv("CONN_URL")

# create connection + session 
engine = create_engine(
    CONN_URL,
    echo=False,
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#############################
#     FAST API DEPENDENCY   #
#############################
def get_db():
    # new db for each request
    db = Session()
    try:
        yield db
    except Exception:
        # rollback if exception occurs before crud commits
        db.rollback()
        raise
    finally:  # runs always
        db.close()

