from PIL import Image
from PIL import ImageTk

class TkinterImage(object):

    def __init__(self, path):
        self.path = path

    def getImage(self):
        return ImageTk.PhotoImage(Image.open(self.path))