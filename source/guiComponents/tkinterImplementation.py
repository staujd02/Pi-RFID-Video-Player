import Tkinter
import tkinter


class TkinterImplementation(object):

    def begin(self, wrappedIdleImage):
        self.root = tkinter.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(
            "{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.config(background='black')
        self.panel = Tkinter.Label(self.root, image=wrappedIdleImage.getImage())
        self.panel.config(background='black')
        self.panel.pack(side='bottom', fill='both', expand='yes')
        self.root.update()

    def update(self):
        self.root.update()

    def changeImage(self, image):
        self.panel.config(image=image)
        self.root.update()
