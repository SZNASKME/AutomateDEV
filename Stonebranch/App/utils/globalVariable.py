

class GlobalVariable(object):
    def __init__(self):
        self._globalVariable = {}
        self._globalWidget = {}
        
    def save(self, key, value):
        self._globalVariable[key] = value

    
    def get(self, key):
        return self._globalVariable.get(key, None)
    
    def getAll(self):
        return self._globalVariable
    
    def remove(self, key):
        if key in self._globalVariable:
            del self._globalVariable[key]
            
    def clear(self):
        self._globalVariable.clear()
        
        
    def saveWidget(self, key, widget):
        self._globalWidget[key] = widget
        
    def getWidget(self, key):
        return self._globalWidget.get(key, None)
    
    def getAllWidget(self):
        return self._globalWidget
    
    def removeWidget(self, key):
        if key in self._globalWidget:
            del self._globalWidget[key]
            
    def clearWidget(self):
        self._globalWidget.clear()
        
    def clearAll(self):
        self._globalVariable.clear()
        self._globalWidget.clear()
        
        