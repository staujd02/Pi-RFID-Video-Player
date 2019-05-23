import unittest
import time

from cardScan import CardScan

class CardScan_test(unittest.TestCase):

    class NoiseMaker(object):
        playedSound = False

        def play(self):
            self.playedSound = True
            return "Boing"

        def didSoundPlay(self):
            return self.playedSound

    class PostiveDummyScanner(object):
        def read_passive_target(self):
            return bytes.fromhex("aaaa")

    class SlowDummyScanner(object):
        timer = None
        triggered = False

        def read_passive_target(self):
            if self.triggered == False:
                self.triggered = True
                self.timer = time.time()
            if (time.time() - self.timer) >= 0.5:
                return bytes.fromhex("aaaa")
            return None

    def test_scan_needs_sound_and_a_scanner_interface(self):
        cardScanner = CardScan(self.NoiseMaker(), self.PostiveDummyScanner())
        self.assertNotEqual(None, cardScanner)

    def test_scan_returns_nothing_when_no_scan_was_run(self):
        cardScanner = CardScan(self.NoiseMaker(), self.PostiveDummyScanner())
        self.assertEqual(None, cardScanner.getFormattedResult())

    def test_scan_can_scan_a_card(self):
        cardScanner = CardScan(self.NoiseMaker(), self.PostiveDummyScanner())
        cardScanner.runScan()

    def test_scan_can_return_the_results_of_a_good_scan(self):
        cardScanner = CardScan(self.NoiseMaker(), self.PostiveDummyScanner())
        cardScanner.runScan()
        self.assertEqual("0xb'aaaa'", cardScanner.getFormattedResult())

    def test_the_scan_is_patient_and_will_wait_a_while_for_a_scan(self):
        cardScanner = CardScan(self.NoiseMaker(), self.SlowDummyScanner())
        cardScanner.runScan()
        self.assertEqual("0xb'aaaa'", cardScanner.getFormattedResult())

    def test_when_a_card_is_scanned_a_sound_plays(self):
        noise = self.NoiseMaker()
        cardScanner = CardScan(noise, self.PostiveDummyScanner())
        cardScanner.runScan()
        self.assertEqual(True, noise.didSoundPlay())