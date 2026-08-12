from SmartApi import SmartConnect
import pyotp
import os
from package.settings.config import API_KEY, CLIENT_CODE, PIN, TOTP_SECRET

def login():
    smartApi = SmartConnect(api_key=API_KEY)
    session = smartApi.generateSession(
        CLIENT_CODE,
        PIN,
        pyotp.TOTP(TOTP_SECRET).now()
    )
    AUTH_TOKEN = session["data"]["jwtToken"]
    FEED_TOKEN = smartApi.getfeedToken()
    return AUTH_TOKEN, FEED_TOKEN, smartApi

    

