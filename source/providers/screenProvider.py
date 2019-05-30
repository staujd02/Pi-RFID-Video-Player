
class ScreenProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def begin(self):
        self.concrete.begin()

    def update(self):
        self.concrete.update()

    def changeImage(self, imageWrapper):
        self.concrete.changeImage(imageWrapper.getImage())