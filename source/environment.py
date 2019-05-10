import logging

class Environment(object):

    ENVIRONMENT_LOG = "environment.log"
    KillCommand = "-255"
    VideoList = "vids.csv"
    UuidTable = "UUID_Table.csv"
    Usb = "< Not Set >"

    def __init__(self, fileName=".env"):
        self.configureLogging()
        self.initializeEnvironment(fileName)

    def configureLogging(self):
        logging.basicConfig(filename=self.ENVIRONMENT_LOG, level=logging.INFO)

    def initializeEnvironment(self, fileName):
        for line in self.readFileByLines(fileName):
            key, value = self.separateKeyValuePair(line)
            setattr(self, key, value)

    def readFileByLines(self, fileName):
        fileContents = self.openEnvironmentStreamOrDefault(fileName)
        lines = fileContents.read().splitlines()
        fileContents.close()
        return lines

    def separateKeyValuePair(self, pair):
        pieces = pair.split('=')
        if self.isNotPair(pieces):
            return "NoAttr", None
        return pieces[0], pieces[1]

    def isNotPair(self, pieces):
        return len(pieces) != 2

    def openEnvironmentStreamOrDefault(self, fileName):
        try:
            return open(fileName, "r")
        except FileNotFoundError:
            logging.warning("No environment file found. Using Defaults...")
            return self.handleMissingEnvironmentFile(fileName)

    def handleMissingEnvironmentFile(self, fileName):
        self.update(fileName)
        return open(fileName, "r")

    def writeLinesToStream(self, stream, lines):
        for line in lines:
            stream.write(line)
        
    def update(self, fileName=".env"):
        stream = open(fileName, "w")
        for key in self.getNonGenericClassMembers():
            stream.write(f"{key}={getattr(self, key)}\n")
        stream.close()
        
    def getNonGenericClassMembers(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))] 
