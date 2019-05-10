import logging
from Tkinter import Frame, StringVar, Label

class WaitPrompt:
    def __init__(self, master):
        # self.load()
        frame = Frame(master)
        frame.pack()
        self.msg = StringVar()
        Label(frame,text='Status').grid(row=0, column=0)
        Label(frame,text=self.msg).grid(row=1, column=0)
        
    def setMsg(self, Message):
        try:
            self.msg.set(str(Message))
            # self.update()
        except Exception as e:
            logging.error('Message ' + str(Message) + ' failed to set.\n' + str(e))

