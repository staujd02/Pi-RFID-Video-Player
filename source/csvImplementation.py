class CSVImplementation(object):

    def init(self):
        self.data = {}

    def load(self, name):
        self.data.clear()
        f = open(name, "r")
        self.readStream(f)
        f.close()

    def readStream(self, stream):
        for line in stream.readlines():
            self.storeLineIntoList(line)

    def storeLineIntoList(self, line):
        entries = line.split(',')
        if self.lastEntryEndsInNewline(entries):
            self.removeLastCharacterFromLastEntry(entries)
        self.data[entries[0]] = entries[1:]

    def lastEntryEndsInNewline(self, entries):
        return entries[-1][-1] == '\n'

    def removeLastCharacterFromLastEntry(self, entries):
        entries[-1] = entries[-1][:-1]

    def save(self):
        pass

    def query(self, key):
        return self.data[key]

    def update(self, key, value):
        self.data[key] = value 