import requests
class Client:
    def __init__(self,API_KEY,API_SIGN,END_POINT):
        self.API_KEY = API_KEY
        self.API_SIGN = API_SIGN
        self.END_POINT = END_POINT # consider to eleminate
    