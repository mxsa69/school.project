import os

class Config:
    # 🔐 Sicherheit
    SECRET_KEY = os.getenv("SECRET_KEY", "deinGeheimerKey123")

    # 💾 Datenbankpfad
    DB_PATH = os.getenv("DB_PATH", os.path.join("instance", "flow_study.db"))
    DATABASE = "flow_data.sqlite"

    # 🍪 Session-Einstellungen
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # True, falls du HTTPS nutzt

    # ⚙️ Vorgaben für die Klassenaktivität
    ACTIVITY_NAME = "Flow-Klassenaktivität"
    ACTIVITY_LEVEL = "mittel"

    # 👩‍💻 Admin-Login
    ADMIN_USER = "masa.sankar"
    ADMIN_PASS = "XXX123"
