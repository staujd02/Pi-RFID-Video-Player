import binascii
import time

class CardScan:

    TIME_OUT = 5
    HEX_CODE_PREFIX = '0x'

    uid = None
    noisy = True
    scanSound = None
    pn532 = None
    
    def __init__(self, scanSound, pn532):
        self.uid = None
        self.noisy = True
        self.scanSound = scanSound
        self.pn532 = pn532

    def runScan(self):
        if self.noisy:
            self.uid = self.noisyScanForCard()
        else:
            self.uid = self.scanForCard()

    def getFormattedResult(self):
        if self.uid:
            return self.HEX_CODE_PREFIX + binascii.hexlify(self.uid)
        return None

    def noisyScanForCard(self):
        uid = self.scanForCard()
        if uid:
            self.scanSound.play()
        return uid

    def scanForCard(self):
        start = time.time()
        uid = None
        while (time.time() - start) < self.TIME_OUT and uid == None:
            uid = self.pn532.read_passive_target()
        return uid