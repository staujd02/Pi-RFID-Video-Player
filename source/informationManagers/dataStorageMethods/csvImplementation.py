class CSVImplementation(object):

    @staticmethod
    def openDB(wrapper, name):
        c = wrapper(CSVImplementation())
        c.init()
        c.load(name)
        return c

    def init(self):
        self.data = {}
    
    def iterate(self):
        return iter(self.data)
    
    def query(self, key):
        return self.data[key]

    def update(self, key, value):
        if not isinstance(value, list):
            value = [value]
        self.data[key] = value
    
    def save(self, name):
        fs = open(name, "w")
        self.__writeDataAsCSV(fs)
        fs.close()

    def load(self, name):
        self.data.clear()
        self.__loadFile(name)

    def __loadFile(self, name):
        f = open(name, "r")
        self.__readStream(f)
        f.close()

    def __readStream(self, stream):
        for line in stream.readlines():
            self.__storeLineIntoList(line)

    def __storeLineIntoList(self, line):
        entries = line.split(',')
        if self.__lastEntryEndsInNewline(entries):
            self.__removeLastCharacterFromLastEntry(entries)
        self.__storeEntriesToData(entries)
    
    def __storeEntriesToData(self, entries):
        if len(entries) == 2:
            self.data[self.__getKey(entries)] = self.__nestSecondItemInAList(entries)
        else:
            self.data[self.__getKey(entries)] = self.__getAListOfAllButTheFirstItem(entries)

    def __getKey(self, entries):
        return entries[0]

    def __getAListOfAllButTheFirstItem(self, entries):
        return entries[1:]

    def __nestSecondItemInAList(self, entries):
        return [entries[1]]

    def __lastEntryEndsInNewline(self, entries):
        return entries[-1][-1] == '\n'

    def __removeLastCharacterFromLastEntry(self, entries):
        entries[-1] = entries[-1][:-1]

    def __writeDataAsCSV(self, fileStream):
        for key in self.data:
            line = self.__getCSVString(key)
            fileStream.write(line)

    def __getCSVString(self, key):
        string = self.__getFirstColumn(key)
        string += self.__getAllButLastColumn(key)
        return string + self.__getLastColumn(key)
    
    def __getFirstColumn(self, key):
        return str(key) + ','

    def __getAllButLastColumn(self, key):
        body = ''
        for item in self.data[key][:-1]:
            body += item + ','
        return body
    
    def __getLastColumn(self, key):
        return self.data[key][-1] + '\n'