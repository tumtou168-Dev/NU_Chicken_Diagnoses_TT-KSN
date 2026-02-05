import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    
    # Fallback to SQLite if DATABASE_URL is not set, to avoid Oracle connection errors during development
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DATABASE_URL") 
        or "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db"))
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False