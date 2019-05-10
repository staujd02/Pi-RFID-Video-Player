class RFIDScannerProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def PN532(self, CS=18, MOSI=23, MISO=24, SCLK=25):
        return self.concrete.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)