import logging

from providers.screenProvider import ScreenProvider
from guiComponents.tkinterImplementation import TkinterImplementation
from guiComponents.tkinterImage import TkinterImage

# Set Up Logging
logging.basicConfig(filename='engine.log',level=logging.INFO)

# Wrap Images
idleImage = TkinterImage('../resources/images/bg.jpg')
brokeImage = TkinterImage('../resources/images/broke.jpg')
brokeLinkImage = TkinterImage('../resources/images/brokenLink.png')

# Load GUI screen
screen = ScreenProvider(TkinterImplementation(idleImage))
screen.begin()

# Load Sounds
pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()
sound = pygame.mixer.Sound(TOUCH_SOUND)
soundBroke = pygame.mixer.Sound(BROKE_SOUND)
sound.set_volume(4)

# Load Keyboard Interface
# Setup MPR121 Hardware
# Setup PN532 Hardware
# Configure GPIO pins
# Read ini file for file names
# Load Video and Card databases