
class Messenger(object):

    def __init__(self, logger, messageDisplay):
        self.logger = logger
        self.messageDisplay = messageDisplay

    def showSaveAndExit(self):
        return self.messageDisplay.askquestion(
            'Save And Quit', 'Would you like to save your changes?')

    def showCardIsNotPaired(self):
        self.messageDisplay.showinfo(
            'Card Unassigned', 'Card is not currently assigned to a video')

    def showCannotPairToInactiveVideos(self):
        self.messageDisplay.showinfo('Video Is Not Active',
                                     'This video\'s file wasn\'t found on the last scan. Please rescan, and pair again.')

    def showCardScannedIsAKiller(self):
        self.messageDisplay.showinfo(
            'Kill Card', 'This card is currently assigned to kill the application.')

    def showDefaultDeviceWarning(self):
        self.messageDisplay.showwarning(
            'No USB Set', 'Please select a USB as a source device and then perform a Scan and Update')
        self.logger.warning('No USB device is set!')

    def displayScanError(self, e):
        self.messageDisplay.showerror('Error Occurred', 'Error: ' + str(e))
        self.logger.error('Scan Failed: ' + str(e))

    def showAbortScanMessage(self):
        self.messageDisplay.showwarning(
            'No Files Found', 'A scan failed to find any files.')
        self.logger.warning('Empty Scan occurred when attempting a merge')

    def showScanErrorMessage(self, e):
        self.messageDisplay.showerror('Scan Failed', 'Scan error: ' + str(e))
        self.logger.error(str(e))

    # def showCurrentDeviceNotFoundWarning(self):
    #     self.messageDisplay.showwarning(
    #         'Missing USB Source', 'WARNING: The current USB repository was not found among the available devices.')
    #     self.logger.warning(
    #         'Current USB repository was not located in device scan!')

    # def terminateWithCurrentDeviceNotFoundMsg(self):
    #     self.messageDisplay.showerror(
    #         'No Devices Detected', 'No devices were detected including the current USB repository.\nPlease inspect USB device, or contact help.')
    #     self.logger.critical('Scanner detected no devices. Closing...')

    # SUGGEST - Removal
    # def terminateWithNoDeviceFailureMessage(self):
    #     self.messageDisplay.showerror(
    #         'Storage Failure', 'No USB devices could be found, this editor will now close.')
    #     self.logger.critical('Failed to find any devices with any media. Closing...')

    # SUGGEST - Removal
    # def showImproperStorageWarning(self):
    #     self.messageDisplay.showerror(
    #         'Improper Storage', 'Media files should not be stored in /media/pi.\nPlease move files to subfolder, or a USB device.')
    #     self.logger.error(
    #         'User error: Files were stored on pi media root. Requested User Action...')