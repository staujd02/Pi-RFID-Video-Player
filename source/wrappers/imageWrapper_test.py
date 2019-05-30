import unittest

from imageWrapper import ImageWrapper

class ImageWrapper_test(unittest.TestCase):

    class testableWrapper(object):
        def getImage(self):
            return "image"

    def test_Image_Wrapper_echos_back_an_image(self):
        iw = ImageWrapper(self.testableWrapper())
        self.assertEqual(iw.getImage(),"image")