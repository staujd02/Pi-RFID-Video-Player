import unittest
import time

from source.wrapper.cardScanWrapper import CardScanWrapper

class CardScanWrapper_test(unittest.TestCase):

    class NoiseMaker(object):
        playedSound = False

        def play(self):
            self.playedSound = True
            return "Boing"

        def didSoundPlay(self):
            return self.playedSound

    class PositiveDummyScanner(object):
        def read_passive_target(self):
            return bytearray([0xaa,0xaa])

    class SlowDummyScanner(object):
        timer = None
        triggered = False

        def read_passive_target(self):
            if self.triggered == False:
                self.triggered = True
                self.timer = time.time()
            if (time.time() - self.timer) >= 0.5:
                return bytearray([0xaa,0xaa])
            return None

    def test_scan_needs_sound_and_a_scanner_interface(self):
        cardScanner = CardScanWrapper(self.NoiseMaker(), self.PositiveDummyScanner())
        self.assertNotEqual(None, cardScanner)

    def test_scan_returns_nothing_when_no_scan_was_run(self):
        cardScanner = CardScanWrapper(self.NoiseMaker(), self.PositiveDummyScanner())
        self.assertEqual(None, cardScanner.getFormattedResult())

    def test_scan_can_scan_a_card(self):
        cardScanner = CardScanWrapper(self.NoiseMaker(), self.PositiveDummyScanner())
        cardScanner.runScan()

    def test_scan_can_return_the_results_of_a_good_scan(self):
        cardScanner = CardScanWrapper(self.NoiseMaker(), self.PositiveDummyScanner())
        cardScanner.runScan()
        self.assertEqual("0xaaaa", cardScanner.getFormattedResult())

    def test_the_scan_is_patient_and_will_wait_a_while_for_a_scan(self):
        cardScanner = CardScanWrapper(self.NoiseMaker(), self.SlowDummyScanner())
        cardScanner.runScan()
        self.assertEqual("0xaaaa", cardScanner.getFormattedResult())

    def test_when_a_card_is_scanned_a_sound_plays(self):
        noise = self.NoiseMaker()
        cardScanner = CardScanWrapper(noise, self.PositiveDummyScanner())
        cardScanner.runScan()
        self.assertEqual(True, noise.didSoundPlay())