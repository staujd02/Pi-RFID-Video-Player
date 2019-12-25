from source.dataStructures import Video, ScanEntry

class Migrator(object):

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

    def __markAllRecordsAsInactive(self):
        keys = list(self.videoDatabase.iterate())
        for key in keys:
            self.__setVideoActiveStatus(key, False)

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
            pass
        # backwards query from title to key
        # ability to insert an entry to the database (probably return the key)

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