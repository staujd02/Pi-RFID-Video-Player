from tkinter import Tk, messagebox, Frame, Label, Entry, Button, Listbox, Scrollbar, Spinbox, END, DISABLED, StringVar, VERTICAL, NORMAL

class EditorGUI:

    def __init__(self, master, events, activeUSB="Unidentified", activeDevices=[], videoNames=[]):
        self.__initializeStringVars()
        self.master = master
        self.activeUSB.set(activeUSB)
        self.activeDevices = activeDevices
        self.initialVideoNames = videoNames
        self.eventDictionary = events

    def start(self):
        self.__createGUIByParts(self.master, self.initialVideoNames)

    def getTextOfCurrentListBoxSelection(self):
        selected = self.videoList.curselection()
        if selected == ():
            return None
        return self.videoList.get(selected)

    def setCurrentCard(self, card):
        self.activeCardNumber.set(card)

    def getCurrentCard(self):
        return self.activeCardNumber.get()

    def startCardScan(self, scanProcess):
        self.readCardButton.config(state=DISABLED, text='Scanning')
        self.readCardButton.update_idletasks()
        scanProcess()
        self.readCardButton.config(state=NORMAL, text='Read Card')

    def clearCurrentSelection(self):
        self.videoList.selection_clear(0, END)

    def currentDeviceName(self):
        return self.deviceSpin.get()

    def setDeviceList(self, devices):
        self.activeDevices.clear()
        for device in devices:
            self.activeDevices.append(device)
        self.updateSpinBox() 

    def updateSpinBox(self):
        self.deviceSpin.config(values=self.activeDevices)
        if len(self.activeDevices) > 0:
            self.setActiveDevice(self.activeDevices[0])

    def setActiveDevice(self, device):
        self.verifyDeviceExistence(device)
        self.deviceSpin.delete(0, END)
        self.deviceSpin.insert(0, device)

    def verifyDeviceExistence(self, device):
        try:
            self.activeDevices.index(device)
        except ValueError:
            raise self.DeviceNotFound(device)

    def setListBoxSelection(self, name):
        i =  self.__getVideoIndexMatchingName(name)
        self.videoList.see(i)
        self.videoList.selection_clear(0, END)
        self.videoList.selection_set(i)
        self.videoList.activate(i)

    def setVideoList(self, newList):
        self.videoList.delete(0, END)
        self.__insertEntries(self.videoList, newList)

    def setDeviceControlText(self, text, enabled = True):
        state = NORMAL if enabled else DISABLED
        self.searchDevicesButton.config(text=text, state=state)
        self.searchDevicesButton.update_idletasks()

    def __initializeStringVars(self):
        self.activeUSB = StringVar()
        self.activeCardNumber = StringVar()

    def __createUSBSpinBox(self, frame, deviceList, activeUSB):
        spin = Spinbox(frame, values=deviceList)
        spin.delete(0, END)
        spin.insert(0, activeUSB)
        spin.grid(row=5, column=0)
        return spin

    def __createGUIByParts(self, master, videoNames):
        self.frame = self.__createMasterFrame(master)
        self.__createLabels(self.frame)
        self.__createButtons(self.frame, self.eventDictionary)
        self.__createHookedGUIElements(self.eventDictionary, videoNames)

    def __createMasterFrame(self, master):
        frame = Frame(master)
        frame.pack()
        return frame

    def __createLabels(self, frame):
        Label(frame, text='RFID Card').grid(row=0, column=0)
        Label(frame, text='Video').grid(row=0, column=2)
        Label(frame, text='Source USB').grid(row=4, column=0)

    def __createButtons(self, frame, events):
        Button(frame, text='Save', command=events.get(
            "save")).grid(row=6, column=2)
        Button(frame, text='Quit', command=events.get(
            "quit")).grid(row=6, column=3)
        Button(frame, text='Assign Kill Code', command=events.get(
            "assignKill")).grid(row=2, column=0)

    def __createHookedGUIElements(self, events, videoNames):
        self.cardLabelBox = self.__createCardEntry(
            self.frame, self.activeCardNumber)
        self.videoList = self.__createVideoListBox(
            self.frame, videoNames, events.get("videoSelectedEvent"))
        self.deviceSpin = self.__createUSBSpinBox(
            self.frame, self.activeDevices, self.activeUSB.get())
        self.readCardButton, self.searchDevicesButton = self.__createStatusButtons(
            self.frame, self.eventDictionary)

    def __createStatusButtons(self, frame, events):
        readCardButton = Button(frame, text='Read Card',
                                command=events.get("beginCardScan"))
        readCardButton.grid(row=1, column=1)
        searchDevicesButton = Button(frame, text='Update Device Repository',
                                     command=events.get("updateRepository"), disabledforeground='blue')
        searchDevicesButton.grid(row=6, column=0)
        return readCardButton, searchDevicesButton

    def __createCardEntry(self, frame, cardNumber):
        e = Entry(frame, textvariable=cardNumber,
                  state=DISABLED, disabledforeground='black')
        e.grid(row=1, column=0)
        return e
    
    def __createListbox(self, frame):
        ls = Listbox(frame)
        ls.grid(row=1, rowspan=5, column=2, columnspan=2)
        return ls

    def __createVideoListBox(self, frame, videoNames, selectEvent):
        videoListbox = self.__createListbox(frame)
        self.__insertEntries(videoListbox, videoNames)
        self.__pairVideoListWithScrollbar(videoListbox)
        videoListbox.bind(
            "<<ListboxSelect>>", lambda event: self.__processListClickEvent(event, selectEvent))
        return videoListbox
    
    def __insertEntries(self, listBox, videoList):
        videoList.sort()
        for entry in videoList:
            listBox.insert(END, entry)
    
    def __pairVideoListWithScrollbar(self, listBox):
        scroll = Scrollbar(listBox, orient=VERTICAL)
        listBox.config(yscrollcommand=scroll.set)
        scroll.config(command=listBox.yview)

    def __processListClickEvent(self, event, observerEventHook):
        videoName = self.getTextOfCurrentListBoxSelection()
        observerEventHook(videoName)

    def __getVideoIndexMatchingName(self, name):
        try:
            return self.videoList.get(0, END).index(name)
        except ValueError:
            raise self.VideoUnavailable(name, "Video was not found in the video list")

    class VideoUnavailable(Exception):

        def __init__(self, requestedVideo, message):
            self.requestedVideo = requestedVideo
            self.message = message
    
    class DeviceNotFound(Exception):

        def __init__(self, device):
            self.device = device
