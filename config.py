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

    # Build Database URI; supports DATABASE_URL (TiDB / managed cloud MySQL / PostgreSQL)
    raw_db_url = os.getenv('DATABASE_URL')
    if raw_db_url:
        # Standardize connection dialect for SQLAlchemy
        if raw_db_url.startswith('mysql://'):
            raw_db_url = 'mysql+pymysql://' + raw_db_url[8:]
        elif raw_db_url.startswith('postgres://'):
            raw_db_url = 'postgresql+psycopg2://' + raw_db_url[11:]
        elif raw_db_url.startswith('postgresql://') and not raw_db_url.startswith('postgresql+'):
            raw_db_url = 'postgresql+psycopg2://' + raw_db_url[13:]

        if 'mysql' in raw_db_url and 'charset=' not in raw_db_url:
            sep = '&' if '?' in raw_db_url else '?'
            raw_db_url = f"{raw_db_url}{sep}charset=utf8mb4"
        SQLALCHEMY_DATABASE_URI = raw_db_url
    elif DB_USER and DB_HOST and DB_NAME:
        ssl_param = ""
        if os.getenv('DB_SSL', '').lower() in ('true', '1', 'required'):
            ssl_param = "&ssl_verify_cert=true"
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4{ssl_param}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///belkhed.db"

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')

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
