import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta")
