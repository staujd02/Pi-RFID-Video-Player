import unittest

from source.providers.screenProvider import ScreenProvider


class ScreenProvider_test(unittest.TestCase):

    class testableImageWrapper(object):
        def getImage(self):
            return "image"

    class testableScreenProvider(object):
        def begin(self):
            pass
        def update(self):
            pass
        def changeImage(self, image):
            self.image = image

    def test_Screen_Provider_can_begin(self):
        sp = ScreenProvider(self.testableScreenProvider())
        sp.begin()

    def test_screen_provider_can_be_updated(self):
        sp = ScreenProvider(self.testableScreenProvider())
        sp.update()

    def test_screen_provider_can_change_its_image(self):
        tSP = self.testableScreenProvider()
        sp = ScreenProvider(tSP)
        sp.changeImage(self.testableImageWrapper())
        self.assertEqual(tSP.image, "image")