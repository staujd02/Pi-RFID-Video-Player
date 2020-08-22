from source.dataStructures import ScanEntry

class Devices(object):

    largestKey = 0

    def __init__(self, fileSearch):
        self.fileSearch = fileSearch

    def getList(self, mediaRoot, scriptFile):
        self.fileSearch.scan(scriptFile, mediaRoot)
        scannedEntries = []
        for entry in self.fileSearch.getList():
            scannedEntries.append(ScanEntry(self.fileSearch.getFile(entry)))
        deviceList = []
        for entry in scannedEntries:
            deviceName = self.extractDeviceNameFromPath(entry.getPath(), mediaRoot)
            if deviceName not in deviceList:
                deviceList.append(deviceName)
        return deviceList
    
    def extractDeviceNameFromPath(self, path, mediaRoot):
        device = path.replace(mediaRoot, '')
        device = device[0:device.find('/')]
        return device