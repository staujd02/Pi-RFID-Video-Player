from tkinter import *
from source.editorPilot import EditorPilot

import pygame
# import Adafruit_PN532 as PN532
import source.standIns.DummyPN532 as PN532

root = Tk()
root.wm_title('RFID Editor')
app = EditorPilot(root, pygame, PN532)
app.init()
root.mainloop()