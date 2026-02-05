import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    
    # Set DATABASE_URL to override (e.g., use SQLite in dev); default is Oracle.
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DATABASE_URL") 
        or "oracle+oracledb://C##IDNS:TOUDEV168@localhost:1521/ORCL")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
