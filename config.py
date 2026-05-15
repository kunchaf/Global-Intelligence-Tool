import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-default"


class Config:
    SECRET_KEY = SECRET_KEY
    DEBUG = True
    # Add other configurations like database URLs here