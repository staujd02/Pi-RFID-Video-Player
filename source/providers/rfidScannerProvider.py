class RFIDScannerProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def PN532(self, CS, MOSI, MISO, SCLK):
        return self.concrete.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
