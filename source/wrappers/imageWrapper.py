class ImageWrapper(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def getImage(self):
        return self.concrete.getImage()