from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/test")

engine = create_engine(DATABASE_URL, echo = True)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
