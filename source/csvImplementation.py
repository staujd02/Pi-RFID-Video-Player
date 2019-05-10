class CSVImplementation(object):

    def init(self):
        self.data = []

    def load(self, name):
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
        self.data.append(entries)

    def lastEntryEndsInNewline(self, entries):
        return entries[-1][-1] == '\n'

    def removeLastCharacterFromLastEntry(self, entries):
        entries[-1] = entries[-1][:-1]

    def save(self):
        pass

    def query(self, command):
        for row in self.data:
            if row[0] == command:
                return row

    def update(self, command):
        pass
