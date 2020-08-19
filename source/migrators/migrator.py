from source.dataStructures import Video, ScanEntry
from source.utilities.devices import Devices

class Migrator(object):

    largestKey = 0

    def __init__(self, fileSearch, videoDatabase, copyMethod, messenger):
        self.fileSearch = fileSearch
        self.videoDatabase = videoDatabase
        self.copyMethod = copyMethod
        self.messenger = messenger
        self.devices = Devices(fileSearch)

    def migrate(self, sourceDeviceName, mediaRoot, scriptFile):
        self.messenger.sendUpdate("Marking all records as inactive...")
        self.messenger.sendUpdate("Scanning...")
        self.__markAllRecordsAsInactive()
        self.messenger.sendUpdate("Scanning media devices...")
        self.__scanAndParse(scriptFile, mediaRoot)
        self.__splitList(sourceDeviceName)
        self.messenger.sendUpdate("Found " + str(len(self.onDevice)) + " record(s) on source device")
        self.messenger.sendUpdate("Found " + str(len(self.notOnDevice)) + " record(s) on non-source devices")
        existingTitles = self.__removeOnDeviceDuplicates()
        self.messenger.sendUpdate(str(len(existingTitles)) + " unique record(s) confirmed on the source device")
        self.__reduceExternalListToNewTitles(existingTitles)
        self.messenger.sendUpdate(str(len(self.notOnDevice)) + " new title(s) discovered")
        self.__updateOnDeviceEntries()
        self.__integrateOffDeviceRecords(sourceDeviceName, mediaRoot)
        self.messenger.sendUpdate("Migration complete")
        self.messenger.sendUpdate("Done")

    def __markAllRecordsAsInactive(self):
        keys = list(self.videoDatabase.iterate())
        for key in keys:
            self.__setVideoActiveStatus(key, False)
            self.__upsertLargestKey(key)
    
    def __upsertLargestKey(self, key):
        numKey = int(key)
        if self.largestKey < numKey:
            self.largestKey = numKey

    def __setVideoActiveStatus(self, key, status):
        entry = Video(self.videoDatabase.query(key))
        entry.setIsActive(status)
        self.videoDatabase.update(key, entry.toList())

    def __scanAndParse(self, scriptFile, mediaRoot):
        self.fileSearch.scan(scriptFile, mediaRoot)
        self.scannedEntries = [ScanEntry(self.fileSearch.getFile(i))
                                for i in self.fileSearch.getList()]
    
    def __splitList(self, sourceDeviceName):
        self.onDevice = []
        self.notOnDevice = []
        for entry in self.scannedEntries:
            if entry.getPath().find(sourceDeviceName, 0) != -1:
                self.onDevice.append(entry)
            else:
                self.notOnDevice.append(entry)

    def __removeOnDeviceDuplicates(self):
        reducedList = [] 
        reducedListTitles = [] 
        for entry in self.onDevice: 
            if entry.getName() not in reducedListTitles: 
                reducedList.append(entry) 
                reducedListTitles.append(entry.getName()) 
        self.onDevice = reducedList
        return reducedListTitles

    def __reduceExternalListToNewTitles(self, reducedListTitles):
        reducedList = [] 
        for entry in self.notOnDevice: 
            if entry.getName() not in reducedListTitles: 
                reducedList.append(entry) 
                reducedListTitles.append(entry.getName()) 
        self.notOnDevice = reducedList
    
    def __updateOnDeviceEntries(self):
        for entry in self.onDevice:
            self.__upsertEntry(entry, True)
    
    def __upsertEntry(self, entry, active):
        index = self.__find(entry)
        if index != -1:
            self.videoDatabase.update(index, [entry.getName(), entry.getPath(), active])
        else:
            self.videoDatabase.update(self.largestKey + 1, [entry.getName(), entry.getPath(), active])
            self.largestKey = self.largestKey + 1
        
    def __find(self, entry):
        for key in self.videoDatabase.iterate():
            video = self.videoDatabase.query(key)
            if Video(video).getName() == entry.getName():
                return key
        return -1
    
    def __integrateOffDeviceRecords(self, sourceDeviceName, mediaRoot):
        for entry in self.notOnDevice:
            key = self.__find(entry)
            if key == -1:
                path = entry.getPath()
                externalDeviceName = self.devices.extractDeviceNameFromPath(path, mediaRoot)
                destination = path.replace(externalDeviceName, sourceDeviceName)
                entry.setPath(destination)
                self.__notifyCopyActivity(entry, path, destination)
                self.copyMethod.copyfile(path, destination)
                self.__upsertEntry(entry, False)
                self.__setVideoActiveStatus(self.largestKey, True)
            else:
                record = Video(self.videoDatabase.query(key))
                path = record.getPath()
                self.__notifyCopyActivity(entry, path, record.getPath())
                self.copyMethod.copyfile(entry.getPath(), record.getPath())
                self.__setVideoActiveStatus(key, True)

    def __notifyCopyActivity(self, entry, path, dest):
        self.messenger.sendMessage("Copying " + str(entry.getName()) + " from " + path + " to " + str(dest))
        self.messenger.sendUpdate("Copying " + str(entry.getName()))
