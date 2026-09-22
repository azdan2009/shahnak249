import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-later")

    # Render يوفر متغير DATABASE_URL تلقائياً لقاعدة PostgreSQL
    # لو ما موجود (تشغيل محلي)، نرجع لـ SQLite كبديل مؤقت فقط
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url:
        # Render أحياناً يرجع postgres:// بدل postgresql:// - نصلحها
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'shahnak.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
