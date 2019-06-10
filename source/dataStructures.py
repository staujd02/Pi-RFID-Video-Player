
class Video(object):

    def __init__(self, var1, var2=None, var3=None):
        if var2 == None or var3 == None:
            self.name = var1[0] 
            self.path = var1[1]
            self.isActive = var1[2]
        else:
            self.__buildFromExplicit(var1, var2, var3)

    def __buildFromExplicit(self, name, path, isActive):
       self.name = name 
       self.path = path
       self.isActive = isActive
    
    def getName(self):
        return self.name
    
    def getPath(self):
        return self.path
    
    def getIsActive(self):
        return self.isActive
