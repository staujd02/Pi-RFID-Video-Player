import board
import digitalio
import adafruit_bitbangio as bitbangio
import busio

class RFIDScannerProvider(object):

    def __init__(self, concrete):
        self.concrete = concrete

    def PN532(self, CS, MOSI, MISO, SCLK):
        cs = digitalio.DigitalInOut(board.D18)
        cs.switch_to_output(value=True)
        spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
        return self.concrete(spi, cs, debug=False)
