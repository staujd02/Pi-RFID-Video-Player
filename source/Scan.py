import subprocess
import os

class Scan:
    
    SCANNER = 'scanner.sh'
    TEMP = 'temp.list'
    
    NAME = []
    PATH = []
    PK = []
    
    scanComplete = False
    
    # Scan results
    contents = []
    
    def __init__(self):
        self.scan()
        self.scanComplete = True
    
    def scan(self):
        del self.NAME[:]
        del self.PATH[:]
        del self.PK[:]
        subprocess.call('../' + self.SCANNER + ' > ' + self.TEMP, shell=True)
        # Load scan output to memory
        f = open(self.TEMP)
        vids = f.read().splitlines()
        f.close()
        if os.path.isfile(self.TEMP):
            os.remove(self.TEMP)
        i=0
        while(i<len(vids)):
            split = vids[i].split(',')
            self.PK.append(int(split[0]))
            self.NAME.append(split[1])
            self.PATH.append(split[2])
            i=i+1