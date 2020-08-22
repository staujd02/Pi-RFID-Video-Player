from source.dataStructures import ScanEntry

class FileManager(object):

    def __init__(self):
        pass

    def handleMissingDataFiles(self, fileList):
        for file in fileList:
            if not os.path.isfile(file):
                open(file, 'a').close() 