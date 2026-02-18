from sqlalchemy import Column, Integer, String, ARRAY
from app.core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    organizer_phone = Column(String, index=True)
    vibe = Column(String)
    participants = Column(ARRAY(String)) # List of phone numbers
    status = Column(String, default="planning")