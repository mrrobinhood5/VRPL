import redis


class RedisClient(redis.Redis):

    def __init__(self, db):
        super().__init__()
        self.host = 'localhost'
        self.port = '6379'
        self.db = db
        self.decode_responses = True


