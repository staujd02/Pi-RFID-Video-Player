import os

class FileManager(object):

    @staticmethod
    def guaranteeListOfFilesExist(fileList):
        for file in fileList:
            if not os.path.isfile(file):
                open(file, 'a').close() 