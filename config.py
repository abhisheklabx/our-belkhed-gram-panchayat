import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-belkhed-dev-secret-key-2026')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'our_belkhed')

    # Build MySQL URI; fallback to sqlite if specified or unavailable
    if DB_USER and DB_HOST and DB_NAME:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///belkhed.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Village Info
    VILLAGE_NAME_EN = os.getenv('VILLAGE_NAME_EN', 'Our Belkhed')
    VILLAGE_NAME_MR = os.getenv('VILLAGE_NAME_MR', 'आपले बेलखेड')
    VILLAGE_LATITUDE = float(os.getenv('VILLAGE_LATITUDE', '19.616556'))
    VILLAGE_LONGITUDE = float(os.getenv('VILLAGE_LONGITUDE', '77.636556'))
    VILLAGE_PIN = os.getenv('VILLAGE_PIN', '445206')
    VILLAGE_TALUKA = os.getenv('VILLAGE_TALUKA', 'Umarkhed')
    VILLAGE_DISTRICT = os.getenv('VILLAGE_DISTRICT', 'Yavatmal')
    VILLAGE_STATE = os.getenv('VILLAGE_STATE', 'Maharashtra')

    # Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # Admin seed defaults
    ADMIN_NAME = os.getenv('ADMIN_NAME', 'Abhishek Thakare')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'abhishek@belkhed.gov.in')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Pass@123')
