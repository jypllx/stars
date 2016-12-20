import sys
import os.path
from openpyxl import Workbook, load_workbook

"""
Manages the mapping betweend the iTunes categories and the Tootal moods.
Uses an 2 column xls file :
 * 1st column : iTunes categories
 * 2nd column : Tootak Moods
"""

class PodMood:
    
    def __init__(self, file):
        if not os.path.exists(file) :
            raise Exception('No file for %s' % file)

        self.file = file
        wb=load_workbook(file)
        ws=wb.active

        self.moods=[]
        self.mapping={}

        line=2
        iCat=ws.cell(row=line, column=2).value

        while iCat is not None:
            mood=ws.cell(row=line, column=1).value
            # print ('R '+str(iCat)+' '+str(mood))
            if mood is not None or mood != '':
                self.moods.append(mood)
                self.mapping[iCat]=mood
            line+=1
            iCat=ws.cell(row=line, column=1).value

        self.moods = list(set(self.moods))

    def get_mood(self, itunes_category):
        try :
            return self.mapping[itunes_category]
        except Exception as e:
            return None

if __name__ == "__main__":
    p = PodMood('./moods.xlsx')