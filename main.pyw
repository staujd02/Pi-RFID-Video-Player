#!/home/athos/repos/bin/python3

from tkinter import *
from source.editorPilot import EditorPilot

import pygame
import Adafruit_PN532 as PN532
from adafruit_pn532.spi import PN532_SPI

root = Tk()
root.wm_title('RFID Editor')
app = EditorPilot(root, pygame, PN532_SPI)
app.init()
root.mainloop()
