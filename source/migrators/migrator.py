from source.dataStructures import Video, ScanEntry

class Migrator(object):

    largestKey = 0

    def __init__(self, fileSearch, videoDatabase, copyMethod):
        self.fileSearch = fileSearch
        self.videoDatabase = videoDatabase
        self.copyMethod = copyMethod

    def migrate(self, sourceDeviceName):
        self.__markAllRecordsAsInactive()
        self.__scanAndParse()
        self.__splitList(sourceDeviceName)
        existingTitles = self.__removeOnDeviceDuplicates()
        self.__reduceExternalListToNewTitles(existingTitles)
        self.__updateOnDeviceEntries()
        self.__integrateOffDeviceRecords(sourceDeviceName)

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

    def __scanAndParse(self):
        self.fileSearch.scan("dummy")
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
    
    def __integrateOffDeviceRecords(self, sourceDeviceName):
        for entry in self.notOnDevice:
            key = self.__find(entry)
            if key == -1:
                path = entry.getPath()
                externalDeviceName = self.__extractDeviceNameFromPath(path)
                destination = path.replace(externalDeviceName, sourceDeviceName)
                entry.setPath(destination)
                self.copyMethod.copyfile(path, destination)
                self.__upsertEntry(entry, False)
                self.__setVideoActiveStatus(self.largestKey, True)
            else:
                record = Video(self.videoDatabase.query(key))
                path = record.getPath()
                self.copyMethod.copyfile(entry.getPath(), record.getPath())
                self.__setVideoActiveStatus(key, True)



    def __extractDeviceNameFromPath(self, path):
        device = path.replace('/media/pi/', '')
        device = device[0:device.find('/')]
        return device

# Scan Result List, Video Database, Copy Location, Source Device

#    -- Scan psudeo --
#    PreflightChecks() ==> is the source usb actually among connected devices?
#    MarkAllRecordsAsInactive()
#    list = ScanAndParse { title, and path parse into video records }
#   (onDevice, notOnDevice) = SplitList(list) ---> sorts between records on device and not
#    notOnDevice = FilterDuplicates(onDevice, notOnDevice) ---> remove records in external devices that also appear in local device 
#                                                            ---> group by title and remove all external references that appear in local
#                                                               ---> otherwise take the first title record
#    for each record onDevice:
#        AddRecordOrFindExisting(record)
#        UpdateFilePath(record)
#        MarkRecordAsActive(record)
#    for each record notOnDevice:
#        cpLocation = AddRecordOrFindExisting(record) -> adds/finds id: returns copy destinatation (does not mark as Active!)
#        Copy(source: record.loc, dst: cpLocation) // copy first so not adding bad records
#        MarkRecordAsActive(record)