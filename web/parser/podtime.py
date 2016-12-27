import sys

class PodTime:
    CATEGORIES = [
        {'id':0, 'name':'0-5min',   'range':[0, 6*60],          'icon':'fa-hourglass-o'},
        {'id':1, 'name':'5-20min',  'range':[6*60,23*60],       'icon':'fa-hourglass-end'},
        {'id':2, 'name':'20min-1h', 'range':[23*60, 65*60],     'icon':'fa-hourglass-half'},
        {'id':3, 'name':'+1h',      'range':[60*60, 1000000000],'icon':'fa-hourglass-start'}]

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

    def getCat(self, duration):
        for cat in self.CATEGORIES:
            if cat['range'][0] <= int(duration) and int(duration) < cat['range'][1]:
                return cat['id']
        raise 'Not Found'
