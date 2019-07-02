
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
    
    def getName(self):
        return self.name
    
    def getPath(self):
        return self.path
    
    def getIsActive(self):
        return self.isActive
