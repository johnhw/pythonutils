from collections import defaultdict
import yaml
import UserDict


class Accumulator(UserDict.DictMixin):
    def __init__(self):
        self.dict = {}
        
    def __getitem__(self, key):           
        if not self.dict.has_key(key):
            self.dict[key] = []
        return self.dict[key]
            
    def __setitem__(self, key, value):                
        v = self[key]
        v.append(value)
        
    def __delitem__(self, key, value):
        if self.dict.hast_key(key):
            del self.dict[key]
            
    def keys(self):
            return self.dict.keys()


class Addressable(UserDict.DictMixin):
    
    def __init__(self):
        self.dict = {}
        
    def __getitem__(self, key):           
        if type(key)==type((1,2)):            
            fkey = key[0]
            result = self.__getitem__(fkey)
            if len(key)==1:
                return result
            else:
                return result[key[1:]]                       
        else:
            if not self.dict.has_key(key):
                self.dict[key] = Addressable()
            return self.dict[key]
            
    def __setitem__(self, key, value):                
        if type(key)==type((1,2)):       
            result = self[key[:-1]]
            result[key[-1]] = value            
        else:
            self.dict[key] = value
        
    def __delitem__(self, key, value):
        if self.dict.hast_key(key):
            del self.dict[key]
            
    def keys(self):
            return self.dict.keys()
            
    def asdictionary(self):
        d = {}
        for key in self.dict:
            if type(self.dict[key])==type(self):
                d[key] = self.dict[key].asdictionary()
            else:   
                d[key] = self.dict[key]
        return d


class Auto(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
        
def dd():
    return defaultdict(defaultdict)
    
d = Addressable()


    

d["cat", "names","usual"] = "pixel"
d["cat", "names","usual"] = "stupid"

d2 = Auto()
d2["cat"]["names"]["usual"] = "stupid"
print yaml.dump(d.asdictionary())

