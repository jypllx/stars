import sys

class PodTime:
    CATEGORIES = [
        {'id':0, 'name':'0-5 min' , 'range':[0, 6*60]},
        {'id':1, 'name':'5-15 min' , 'range':[6*60,16*60]},
        {'id':2, 'name':'15-30 min', 'range':[16*60, 35*60]},
        {'id':3, 'name':'30-60 min', 'range':[35*60, 67*60]},
        {'id':5, 'name':'+60 min'  , 'range':[60*60, 1000000000]}]

    def getDurationCat(self, duration_str):
        try :
            h, m, s = duration_str.split(':')
        except:
            h = 0
            m, s = duration_str.split(':')
        
        duration = int(h)*3600 + int(m)*60 + int(s)

        for cat in self.CATEGORIES:
            if cat['range'][0] <= duration and duration < cat['range'][1]:
                return duration, cat['id'], cat['name']

    def getCat(duration):
        
        for cat in self.CATEGORIES:
            if cat['id'] == name :
                return cat['id']
        raise 'Not Found'