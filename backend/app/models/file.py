from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.models import Base

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    path = Column(String, nullable=False)
    converted_pptx_path = Column(String, nullable=True)
    conversion_status = Column(String, default="pending")

    user = relationship('User', back_populates='files') 