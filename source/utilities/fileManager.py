import os

class FileManager(object):

    @staticmethod
    def guaranteeListOfFilesExist(listOfFileNames):
        for fileName in listOfFileNames:
            FileManager.guaranteeFileExist(fileName)

    @staticmethod
    def guaranteeFileExist(fileName):
        open(fileName, 'a').close() 