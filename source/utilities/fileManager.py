import os

class FileManager(object):

    @staticmethod
    def guaranteeListOfFilesExist(listOfFileNames):
        for fileName in listOfFileNames:
            self.guaranteeFileExist(fileName)

    @staticmethod
    def guaranteeFileExist(fileName):
        open(fileName, 'a').close() 