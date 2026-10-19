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

    # Build Database URI; supports DATABASE_URL (TiDB / managed cloud MySQL / PostgreSQL / CLI string)
    @staticmethod
    def build_database_uri():
        import re
        import urllib.parse
        from sqlalchemy.engine.url import make_url

        raw = os.getenv('DATABASE_URL', '').strip().strip("'\"")

        # Handle case where user pasted the mysql CLI command string
        if raw and ('mysql ' in raw or ('-h ' in raw and '-u ' in raw)):
            u_m = re.search(r"-u\s+['\"]?([^'\"\s]+)['\"]?", raw)
            h_m = re.search(r"-h\s+['\"]?([^'\"\s]+)['\"]?", raw)
            P_m = re.search(r"-P\s+['\"]?(\d+)['\"]?", raw)
            D_m = re.search(r"-D\s+['\"]?([^'\"\s]+)['\"]?", raw)
            p_m = re.search(r"-p['\"]?([^'\"\s]+)['\"]?", raw)

            u = u_m.group(1) if u_m else ''
            h = h_m.group(1) if h_m else ''
            P = P_m.group(1) if P_m else '4000'
            D = D_m.group(1) if D_m else 'our_belkhed'
            p = p_m.group(1) if p_m else ''
            if p in ('<PASSWORD>', 'PASSWORD'):
                p = os.getenv('DB_PASSWORD', '')

            q_u = urllib.parse.quote_plus(u)
            q_p = urllib.parse.quote_plus(p)
            raw = f"mysql+pymysql://{q_u}:{q_p}@{h}:{P}/{D}?charset=utf8mb4&ssl_verify_cert=true"

        if raw:
            # Standardize connection dialect for SQLAlchemy
            if raw.startswith('mysql://'):
                raw = 'mysql+pymysql://' + raw[8:]
            elif raw.startswith('postgres://'):
                raw = 'postgresql+psycopg2://' + raw[11:]
            elif raw.startswith('postgresql://') and not raw.startswith('postgresql+'):
                raw = 'postgresql+psycopg2://' + raw[13:]

            if 'mysql' in raw and 'charset=' not in raw:
                sep = '&' if '?' in raw else '?'
                raw = f"{raw}{sep}charset=utf8mb4"

            # Auto-enable SSL for TiDB Cloud Serverless
            if ('tidbcloud.com' in raw or ':4000' in raw) and 'ssl' not in raw.lower():
                sep = '&' if '?' in raw else '?'
                raw = f"{raw}{sep}ssl_verify_cert=true"

            try:
                make_url(raw)
                return raw
            except Exception as e:
                print(f"Warning: Could not parse DATABASE_URL directly ({e}), checking fallback...")

        # Fallback to individual DB_* parameters
        db_user = os.getenv('DB_USER', 'root')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'our_belkhed')
        db_pass = os.getenv('DB_PASSWORD', '')

        if db_user and db_host and db_name:
            q_u = urllib.parse.quote_plus(db_user)
            q_p = urllib.parse.quote_plus(db_pass)
            ssl_param = ""
            if os.getenv('DB_SSL', '').lower() in ('true', '1', 'required') or 'tidbcloud.com' in db_host:
                ssl_param = "&ssl_verify_cert=true"
            return f"mysql+pymysql://{q_u}:{q_p}@{db_host}:{db_port}/{db_name}?charset=utf8mb4{ssl_param}"

        return "sqlite:///belkhed.db"

    SQLALCHEMY_DATABASE_URI = build_database_uri()

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
