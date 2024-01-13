## A class for quickly search keywords in a list
class searchableList:
    def __init__(self, *args):
        self.mylist = args
        for arg in args:
            setattr(self, arg, arg)
    def contains(self, value):
        # find value in self.mylist
        if(value in self.mylist):
            return True
        else:
            return False
    def allValues(self):
        return self.mylist
    
    def __str__(self):
        return str(self.mylist)
    
    def __repr__(self):
        return str(self.mylist)
    
    def __getitem__(self, key):
        return self.mylist[key]

class searchableDict:
    def __init__(self, kwargs):
        self.mydict = kwargs
        for key in kwargs:
            setattr(self, key, key)
    def contains(self, value):
        # find value in self.mylist
        if(value in self.mydict):
            return True
        else:
            return False
    def __str__(self):
        return str(self.mydict)
    
    def __repr__(self):
        return str(self.mydict)
    
    def __getitem__(self, key):
        return self.mydict[key]


Language = searchableList('af', 'am', 'an', 'ar', 'as', 'az', 'be', 'bg', 'bn', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'dz', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 'ga', 'gl', 'gu', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jv', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'nb', 'ne', 'nl', 'nn', 'no', 'oc', 'or', 'pa', 'pl', 'ps', 'pt', 'qu', 'ro', 'ru', 'rw', 'se', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'ug', 'uk', 'ur', 'vi', 'vo', 'wa', 'xh', 'zh', 'zu')
