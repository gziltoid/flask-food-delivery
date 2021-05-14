import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_URI = os.getenv("DATABASE_URL")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)


class Config:
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
