from package.helper.login import login
from package.settings.config import API_KEY, CLIENT_CODE



class Client():
    def __init__(self):
        self.smartApi = None
        self.auth_token = None
        self.feed_token = None

    def login(self):
        self.auth_token, self.feed_token, self.smartApi = login()

    def fetch_ltp(self, exchange="NSE", tradingsymbol="IDEA-EQ", symboltoken="14366"):
        response = self.smartApi.ltpData(
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            symboltoken=symboltoken
        )
        return response

    def create_sws(self):
        from SmartApi.smartWebSocketV2 import SmartWebSocketV2
        auth_token, feed_token = self.auth_token, self.feed_token
        sws = SmartWebSocketV2(auth_token, API_KEY, CLIENT_CODE, feed_token)
    
        return sws


if __name__ == "__main__":
    ltp = Client().fetch_ltp()
    print(ltp)