class Migrator(object):

    def __init__(self):
        pass

# Scan Result List, Video Database, Copy Location, Source Device

# -----> Create one test service, initial master list state --> end state (track copy calls)
#  --: Cases :--
#       Record in MasterList and not on local device, but is on external device (0,1)
#       Record in MasterList and not on any device (0,0)
#       Record in MasterList and on local device and on external device (1,1)
#       Record in MasterList and only on local device (1,0)
#       Record in MasterList and on local device, different location and on external device
#       Record in MasterList and only on local device, different location
#       Record not in MasterList and not on local device, but is on external device (0,1)
#       Record not in MasterList and on local device and on external device (1,1)
#       Record not in MasterList and only on local device (1,0)

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