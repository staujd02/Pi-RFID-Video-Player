import board
import digitalio
import adafruit_bitbangio as bitbangio

class RFIDScannerProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def PN532(self, CS, MOSI, MISO, SCLK):
        cs = digitalio.DigitalInOut(board.D18)
        cs.switch_to_output(value=True)
        spi = bitbangio.SPI(board.D25, MOSI=board.D23, MISO=board.D24)
        return self.concrete(spi, cs, debug=False)
