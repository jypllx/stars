import sys

class PodTime:
    CATEGORIES = [
        {'cat':0, 'name':'From 0 to 10 min' , 'range':[0, 13*60]},
        {'cat':1, 'name':'From 10 to 30 min', 'range':[13*60, 35*60]},
        {'cat':2, 'name':'From 30 to 60 min', 'range':[35*60, 67*60]},
        {'cat':3, 'name':'Over 60 min'      , 'range':[60*60, 1000000000]}]

    def getDurationCat(self, duration_str):
        try :
            h, m, s = duration_str.split(':')
        except:
            h = 0
            m, s = duration_str.split(':')
        
        duration = int(h)*3600 + int(m)*60 + int(s)

        for cat in self.CATEGORIES:
            if cat['range'][0] <= duration and duration < cat['range'][1]:
                return duration, cat['cat']


if __name__ == '__main__':
    print(str(PodTime().getDurationCat(sys.argv[1])))