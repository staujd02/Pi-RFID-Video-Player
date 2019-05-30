class SoundProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete
        self.mixer = concrete.mixer

    def init(self):
        return self.concrete.init()
    