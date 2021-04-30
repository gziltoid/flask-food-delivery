import os

from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy

from views import app

load_dotenv(find_dotenv())

DB_URI = os.getenv("DATABASE_URL")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

app.config.update(
    DEBUG=False,
    SQLALCHEMY_ECHO=False,
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run()
