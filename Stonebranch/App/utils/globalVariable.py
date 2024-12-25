

class GlobalVariable(object):
    def __init__(self):
        self._globalVariable = {}
        
    def set(self, key, value):
        self._globalVariable[key] = value
        
    def get(self, key):
        return self._globalVariable.get(key, None)
    
    def remove(self, key):
        if key in self._globalVariable:
            del self._globalVariable[key]
            
    def clear(self):
        self._globalVariable.clear()
    
        