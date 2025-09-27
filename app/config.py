import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hotel_agent.db")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Booking.com API
    BOOKING_API_KEY: str = os.getenv("BOOKING_API_KEY", "")
    BOOKING_API_URL: str = os.getenv("BOOKING_API_URL", "https://distribution-xml.booking.com/2.5/json")
    
    # Airbnb API
    AIRBNB_API_KEY: str = os.getenv("AIRBNB_API_KEY", "")
    AIRBNB_API_URL: str = os.getenv("AIRBNB_API_URL", "https://api.airbnb.com/v2")
    
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "Hotel Response Agent")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()