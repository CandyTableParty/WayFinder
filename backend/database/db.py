from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_URL = os.getenv("DB_URL")

engine = create_engine(
    DB_URL,
    connect_args={"ssl": {"ssl": True}},  # TiDB Serverless는 SSL 필수
    pool_recycle=3600
)