class Database(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def init(self):
        self.concrete.init()

    def load(self, databaseName):
        self.concrete.load(databaseName)

    def save(self):
        self.concrete.save()

    def query(self, command):
        return self.concrete.query(command)
    
    def update(self, command):
        self.concrete.update(command)