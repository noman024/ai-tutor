from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User
from .file import File 