import logging

class Environment(object):

    DEFAULT_Usb = "< Not Set >"

    ENVIRONMENT_LOG = "environment.log"
    SCAN_SOUND = '../resources/sound/ambi_soft_buzz.flac'
    MEDIA_ROOT = '/media/pi/'
    SCAN_SCRIPT = 'scanner.sh'
    KillCommand = "-255"
    VideoList = "../data/vids.csv"
    LinkedTable = "../data/CardsToVideos.csv"
    Usb = DEFAULT_Usb
    CHIP_SELECT_PIN = "18"
    MASTER_OUTPUT_SLAVE_INPUT_PIN = "23"
    MASTER_INPUT_SLAVE_OUTPUT_PIN = "24"
    SERIAL_CLOCK_PIN = "25"

    def __init__(self, fileName=".env"):
        self.__configureLogging()
        self.__initializeEnvironment(fileName)


    def readFileByLines(self, fileName):
        fileContents = self.__openEnvironmentStreamOrDefault(fileName)
        lines = fileContents.read().splitlines()
        fileContents.close()
        return lines

    def update(self, fileName=".env"):
        stream = open(fileName, "w")
        for key in self.__getNonGenericClassMembers():
            stream.write(key + "=" + getattr(self, key) + "\n")
        stream.close()

    def __openEnvironmentStreamOrDefault(self, fileName):
        try:
            return open(fileName, "r")
        except FileNotFoundError:
            logging.warning("No environment file found. Using Defaults...")
            return self.__handleMissingEnvironmentFile(fileName)

    def __initializeEnvironment(self, fileName):
        for line in self.readFileByLines(fileName):
            key, value = self.__separateKeyValuePair(line)
            setattr(self, key, value)
    
    def __configureLogging(self):
        logging.basicConfig(filename=self.ENVIRONMENT_LOG, level=logging.INFO)

    def __separateKeyValuePair(self, pair):
        pieces = pair.split('=')
        if self.__isNotPair(pieces):
            return "NoAttr", None
        return pieces[0], pieces[1]

    def __isNotPair(self, pieces):
        return len(pieces) != 2

    def __handleMissingEnvironmentFile(self, fileName):
        self.update(fileName)
        return open(fileName, "r")
        
    def __getNonGenericClassMembers(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))] 
