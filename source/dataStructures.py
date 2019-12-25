
class Video(object):

    def __init__(self, arg1, arg2=None, arg3=None):
        if arg2 == None or arg3 == None:
            self.__extractVideoFromList(arg1)
        else:
            self.__mapArgumentsToMembers(arg1, arg2, arg3)

    def __extractVideoFromList(self, list):
        self.name = list[0] 
        self.path = list[1]
        self.isActive = bool(list[2])

    def __mapArgumentsToMembers(self, name, path, isActive):
       self.name = name 
       self.path = path
       self.isActive = isActive

    def toList(self):
        return [self.name, self.path, self.isActive]
    
    def getName(self):
        return self.name
    
    def getPath(self):
        return self.path
    
    def getIsActive(self):
        return self.isActive
    
    def setName(self, name):
        self.name = name
    
    def setPath(self, path):
        self.path = path
    
    def setIsActive(self, isActive):
        self.isActive = isActive

class ScanEntry(object):

    def __init__(self, arg1, arg2=None, arg3=None):
        if arg2 == None or arg3 == None:
            self.__extractEntryFromList(arg1)
        else:
            self.__mapArgumentsToMembers(arg1, arg2, arg3)

    def __extractEntryFromList(self, list):
        self.id = list[0] 
        self.name = list[1]
        self.path = list[1]

    def __mapArgumentsToMembers(self, id, name, path):
       self.id = id
       self.name = name 
       self.path = path

    def toList(self):
        return [self.id, self.name, self.path]
    
    def getName(self):
        return self.name
    
    def getPath(self):
        return self.path
    
    def getId(self):
        return self.id
    
    def setName(self, name):
        self.name = name
    
    def setPath(self, path):
        self.path = path
    
    def setId(self, id):
        self.id = id