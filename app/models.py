from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Hotel(Base):
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String(100))
    country = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, nullable=False)
    guest_name = Column(String(255))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    room_type = Column(String(100))
    guest_count = Column(Integer)
    booking_reference = Column(String(100), unique=True)
    status = Column(String(50), default="confirmed")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GuestMessage(Base):
    __tablename__ = "guest_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, nullable=False)
    platform = Column(String(50))  # booking.com, airbnb, etc.
    message_content = Column(Text, nullable=False)
    message_type = Column(String(50))  # question, complaint, request
    timestamp = Column(DateTime, default=func.now())
    is_processed = Column(Boolean, default=False)

class ResponseTemplate(Base):
    __tablename__ = "response_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, nullable=False)
    message_type = Column(String(50), nullable=False)
    template_content = Column(Text, nullable=False)
    language = Column(String(10), default="ja")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ResponseLog(Base):
    __tablename__ = "response_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    guest_message_id = Column(Integer, nullable=False)
    response_content = Column(Text, nullable=False)
    response_type = Column(String(50))  # automated, manual
    sent_at = Column(DateTime, default=func.now())
    is_sent = Column(Boolean, default=False)

class NearbyAttraction(Base):
    __tablename__ = "nearby_attractions"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # restaurant, tourist_spot, shopping, etc.
    distance_km = Column(Float)
    rating = Column(Float)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())