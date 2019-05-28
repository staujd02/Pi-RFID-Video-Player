import logging

from screenProvider import ScreenProvider
from tkinterImplementation import TkinterImplementation
from tkinterImage import TkinterImage

# Set Up Logging
logging.basicConfig(filename='engine.log',level=logging.INFO)

# Wrap Images
idleImage = TkinterImage('../bg.jpg')
brokeImage = TkinterImage('../broke.jpg')
brokeLinkImage = TkinterImage('../brokenLink.png')

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