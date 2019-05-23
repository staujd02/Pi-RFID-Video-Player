class Database(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def init(self):
        self.concrete.init()

    def load(self, databaseName):
        self.concrete.load(databaseName)

    def save(self):
        self.concrete.save()

    def query(self, key):
        return self.concrete.query(key)
    
    def update(self, key, value):
        self.concrete.update(key, value)