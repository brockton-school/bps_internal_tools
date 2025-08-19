# bps_internal_tools/extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from authlib.integrations.flask_client import OAuth

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
oauth = OAuth()