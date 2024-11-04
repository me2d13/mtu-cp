
SK_IP_ADDRESS = "ip"

class MtuState:
    def __init__(self):
        self.data = dict()

    def get(self, key):
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value

