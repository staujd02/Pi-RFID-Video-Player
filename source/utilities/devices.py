from source.dataStructures import ScanEntry

class Devices(object):

    largestKey = 0

    def __init__(self, fileSearch):
        self.fileSearch = fileSearch
    
    def extractDeviceNameFromPath(self, path, mediaRoot):
        device = path.replace(mediaRoot, '')
        device = device[0:device.find('/')]
        return device

    def getList(self, mediaRoot, scriptFile):
        self.fileSearch.scan(scriptFile, mediaRoot)
        scannedEntries = self.__extractScannedEntries()
        return self.__convertScannedEntriesToDeviceList(scannedEntries, mediaRoot)

    def __extractScannedEntries(self):
        scannedEntries = []
        for entry in self.fileSearch.getList():
            self.__addValidEntries(scannedEntries, entry)
        return scannedEntries

    def __addValidEntries(self, scannedEntries, entry):
        file = self.fileSearch.getFile(entry)
        if len(file) > 1:
            scannedEntries.append(ScanEntry(file))

    def __convertScannedEntriesToDeviceList(self, scannedEntries, mediaRoot):
        deviceList = []
        for entry in scannedEntries:
            deviceName = self.extractDeviceNameFromPath(entry.getPath(), mediaRoot)
            self.__addDevice(deviceList, deviceName)
        return deviceList

    def __addDevice(self, deviceList, deviceName):
        if deviceName not in deviceList:
            deviceList.append(deviceName)
