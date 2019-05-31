from tkinter import Tk, messagebox, Frame, Label, Entry, Button, Listbox, Scrollbar, Spinbox, END, DISABLED, StringVar, VERTICAL, NORMAL

class EditorGUI:

    def __init__(self, master, activeUSB, activeDevices, videoNames, events):
        self.initializeStringVars()
        self.master = master
        self.activeUSB.set(activeUSB)
        self.activeDevices = activeDevices
        self.initialVideoNames = videoNames
        self.eventDictionary = events
    
    def initializeStringVars(self):
        self.activeUSB = StringVar()
        self.activeCardNumber = StringVar()

    def start(self):
        self.createGUIByParts(self.master, self.initialVideoNames)

    def createUSBSpinBox(self, frame, deviceList, activeUSB):
        spin = Spinbox(frame, values=deviceList)
        spin.delete(0, END)
        spin.insert(0, activeUSB)
        spin.grid(row=5, column=0)
        return spin

    def createGUIByParts(self, master, videoNames):
        self.frame = self.createMasterFrame(master)
        self.createLabels(self.frame)
        self.createButtons(self.frame, self.eventDictionary)
        self.createHookedGUIElements(self.eventDictionary, videoNames)

    def createMasterFrame(self, master):
        frame = Frame(master)
        frame.pack()
        return frame

    def createLabels(self, frame):
        Label(frame, text='RFID Card').grid(row=0, column=0)
        Label(frame, text='Video').grid(row=0, column=2)
        Label(frame, text='Source USB').grid(row=4, column=0)

    def createButtons(self, frame, events):
        Button(frame, text='Save', command=events.get(
            "save")).grid(row=6, column=2)
        Button(frame, text='Quit', command=events.get(
            "quit")).grid(row=6, column=3)
        Button(frame, text='Assign Kill Code', command=events.get(
            "assignKill")).grid(row=2, column=0)

    def createHookedGUIElements(self, events, videoNames):
        self.cardLabelBox = self.createCardEntry(
            self.frame, self.activeCardNumber)
        self.videoList = self.createVideoListBox(
            self.frame, videoNames, events.get("videoSelectedEvent"))
        self.spin = self.createUSBSpinBox(self.frame, self.activeDevices, self.activeUSB.get())
        self.readCardButton, self.searchDevicesButton = self.createStatusButtons(
            self.frame, self.eventDictionary)

    def createStatusButtons(self, frame, events):
        readCardButton = Button(frame, text='Read Card',
                                command=events.get("beginCardScan"))
        readCardButton.grid(row=1, column=1)
        searchDevicesButton = Button(frame, text='Update Device Repository',
                                   command=events.get("updateRepository"), disabledforeground='blue')
        searchDevicesButton.grid(row=6, column=0)
        return readCardButton, searchDevicesButton

    def createCardEntry(self, frame, cardNumber):
        e = Entry(frame, textvariable=cardNumber,
                  state=DISABLED, disabledforeground='black')
        e.grid(row=1, column=0)
        return e

    def createVideoListBox(self, frame, videoNames, selectEvent):
        videoListbox = self.createListbox(frame)
        self.insertEntries(videoListbox, videoNames)
        self.pairVideoListWithScrollbar(videoListbox)
        videoListbox.bind("<<ListboxSelect>>", lambda event: self.processListClickEvent(event, selectEvent))
        return videoListbox

    def processListClickEvent(self, event, observerEventHook):
        videoName = self.getTextOfCurrentListBoxSelection()
        observerEventHook(videoName)

    def getTextOfCurrentListBoxSelection(self):
        selected = self.videoList.curselection()
        print(selected)
        if selected == ():
            return None
        return self.videoList.get(selected)

    def createListbox(self, frame):
        ls = Listbox(frame)
        ls.grid(row=1, rowspan=5, column=2, columnspan=2)
        return ls

    def insertEntries(self, listBox, videoList):
        for entry in videoList:
            listBox.insert(END, entry)

    def pairVideoListWithScrollbar(self, listBox):
        scroll = Scrollbar(listBox, orient=VERTICAL)
        listBox.config(yscrollcommand=scroll.set)
        scroll.config(command=listBox.yview)
    
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

    # def processCard(self, scan):
    #     # Scans RFID cards and sets them to text box
    #     try:
    #         self.processResult(scan)
    #     except Exception as e:
    #         self.displayScanError(e)

    # def processResult(self, scanResult):
    #     if scanResult == None:
    #         return
    #     self.activeCardNumber.set(scanResult)     # Populate text box
    #     self.deselectActiveListboxItems()
    #     self.linkCardWithListbox(scanResult)

    # def deselectActiveListboxItems(self):
    #     # De-select any active items in listbox
    #     self.videoList.selection_clear(0, END)

    # def linkCardWithListbox(self, scanResult):
    #     index = self.verifyCard(scanResult)
    #     if str(self.uuidFK[index]) == self.environment.KillCommand:
    #         messagebox.showinfo(
    #             'Kill Card', 'This card is currently assigned to kill the application.')
    #         return
    #     self.highlightItemInListbox(index)

    # def highlightItemInListbox(self, index):
    #     try:
    #         i = self.vidPK.index(self.uuidFK[index])
    #     except:
    #         messagebox.showinfo('Card Unassigned',
    #                             'Card is not currently assigned to a video')
    #     else:
    #         self.videoList.see(i)
    #         self.videoList.selection_clear(0, END)
    #         self.videoList.selection_set(i)
    #         self.videoList.activate(i)

    # def verifyCard(self, uidt):
    #     try:
    #         uuidIndex = self.uuid.index(uidt)
    #     except:
    #         uuidIndex = self.addNewCard(uidt)
    #     return uuidIndex

    # def refreshListBox(self):
    #     self.videoList.delete(0, END)
    #     for entry in self.vidNAME:
    #         self.videoList.insert(END, entry)

    # def newselection(self, event):
    #     # Fires when a new item is selected in the listbox
    #     selection = event.widget.curselection()
    #     try:
    #         txt = self.cardLabelBox.get()
    #         if txt == '':
    #             return
    #         i = self.uuid.index(txt)
    #         self.uuidFK[i] = self.vidPK[selection[0]]
    #     except Exception as e:
    #         messagebox.showerror('Error During Set', 'Error: ' + str(e))
    #         logging.error(str(e))

    # def createKiller(self):
    #     try:
    #         self.assignCurrentCardAsKiller()
    #         self.videoList.selection_clear(0, END)
    #     except Exception as e:
    #         self.handleCardNotScannedError(e)

    # def assignCurrentCardAsKiller(self):
    #     i = self.uuid.index(self.cardLabelBox.get())
    #     self.uuidFK[i] = int(self.environment.KillCommand)
