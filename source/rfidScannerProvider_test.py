import unittest

from rfidScannerProvider import RFIDScannerProvider

class RFIDScannerProvider_test(unittest.TestCase):

    def test_theClassCanBeInitialized(self):
        rfid = RFIDScannerProvider(testable())
        self.assertEqual(f"Hooked to 1, 4, 2, 3", rfid.PN532(1,2,3,4))
        
class testable(object):

    def PN532(self, cs=11, sclk=22, mosi=11, miso=55):
        return f"Hooked to {cs}, {sclk}, {mosi}, {miso}"
    