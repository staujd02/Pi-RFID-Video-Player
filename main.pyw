from tkinter import *
from source.editorPilot import EditorPilot

import pygame
# import Adafruit_PN532 as PN532

class DummyRFID(object):

    class StandInPN532(object):
        i = 0
        loop = [
            bytearray([0xb3,0xff,0x25,0x5d]),
            bytearray([0xb1,0xff,0x25,0x5d]),
            bytearray([0xbf,0xff,0x25,0x5d]),
        ]

        def begin(self):
            pass
        def SAM_configuration(self):
            pass
        def read_passive_target(self):
            self.i = self.i + 1
            if self.i == 3:
                self.i = 0
            return self.loop[self.i]

    def PN532(self, cs=11, sclk=22, mosi=11, miso=55):
        return self.StandInPN532()

root = Tk()
root.wm_title('RFID Editor')
app = EditorPilot(root, pygame, DummyRFID())
app.init()
root.mainloop()