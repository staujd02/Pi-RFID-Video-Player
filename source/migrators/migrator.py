class Migrator(object):

    def __init__(self, fileSearch, videoDatabase, copyMethod):
        self.fileSearch = fileSearch
        self.videoDatabase = videoDatabase
        self.copyMethod = copyMethod

    def migrate(self, sourceDeviceName):
        pass

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
#        UpdateFilePath(record)
#        MarkRecordAsActive(record)
#    for each record notOnDevice:
#        cpLocation = AddRecordOrFindExisting(record) -> adds/finds id: returns copy destinatation (does not mark as Active!)
#        Copy(source: record.loc, dst: cpLocation) // copy first so not adding bad records
#        MarkRecordAsActive(record)