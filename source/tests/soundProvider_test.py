import unittest

from source.providers.soundProvider import SoundProvider

class SoundProvider_test(unittest.TestCase):

    def test_theClassCanBeInitialized(self):
        sound = SoundProvider(testable())
        self.assertEqual("I can quack", sound.init())
    
    def test_the_mixer_object_is_accessible(self):
        sound = SoundProvider(testable())
        self.assertEqual("Loud quack", sound.mixer.quack("Loud"))


class testable(object):

    class Mixer(object):

        def quack(self, volume):
            return volume + " quack"
    
    mixer = Mixer()

    def init(self):
        return "I can quack"
    