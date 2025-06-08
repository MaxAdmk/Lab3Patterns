class Trade:
    def __init__(self, id, asset_name, type, timestamp, value):
        self.id = id
        self.type = type
        self.asset_name = asset_name
        self.timestamp = timestamp
        self.value = value

class Asset:
    def __init__(self, id, name, type, timestamp, current_price):
        self.id = id
        self.type = type
        self.name = name
        self.timestamp = timestamp
        self.current_price = current_price