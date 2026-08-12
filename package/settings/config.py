import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
PIN = os.getenv("PIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")


