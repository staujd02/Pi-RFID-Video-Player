from Tkinter import *
from editor import Editor

import pygame
import Adafruit_Python_PN532 as PN532

root = Tk()
root.wm_title('RFID Editor')
app = Editor(root, pygame, PN532)
root.mainloop()