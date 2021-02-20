import xlrd
import os
import sys
import datetime

from appPublic.strUtils import *

TCS={
    'int':int,
    'float':float,
    'str':str,
}

def isEmptyCell(cell):
    return cell.ctype == xlrd.XL_CELL_EMPTY

def isCommentValue(v):
    if type(v)==type('') and v[0] == '#':
        return True
    return False

def purekey(k):
    return k.split(':')[0]
        
def castedValue(v,k):
    ki = k.split(':')
    if len(ki)<2 or v is None:
        return v
    ki = ki[1:]
    if 'list' in ki:
        if type(v) == type(''):
            v = v.split(',')
        elif type(v) != type([]):
            v = [v]
    
    for k,tc in TCS.items():
        if k in ki:
            if type(v) == type([]):
                return [ tc(i) for i in v ]
            else:
                return tc(v)
    return v
    
class ExcelData:
    _indictors = {
        ':__dict__':'ff',
        ':__list__':'ff',
        ':__include__':'ff',
    }
    
    def __init__(self,xlsfile,encoding='UTF8',startrow=0,startcol=0):
        self._book = xlrd.open_workbook(xlsfile)
        self.encoding = encoding
        self._filename = xlsfile
        self.startrow=0
        self.startcol=0
        self._dataset = self.dataload()
    
    def __del__(self):
        del self._book
        del self._dataset
        
    def cellvalue(self,sheet,x,y):
        if sheet.cell_type(x,y)==xlrd.XL_CELL_EMPTY:
            return None
        if sheet.cell_type(x,y)==xlrd.XL_CELL_DATE:
        	y,m,d,hh,mm,ss = xlrd.xldate_as_tuple(sheet.cell_value(x,y),self._book.datemode)
        	return datetime.date(y,m,d)
        s = sheet.cell_value(x,y)
        return self.trimedValue(s)
        
    def isCommentCell(self,cell):
        if isEmptyCell(cell):
            return False
        v = self.trimedValue(cell.value)
        return isCommentValue(v)
        
    def dateMode(self):
        return self._book.datemode
        
    def trimedValue(self,v):
        if type(v) == type(u' '):
            v = v.encode(self.encoding)
        if type(v) == type(''):
            v = lrtrim(v)
        return v
    def dataload(self):
        dat = {}
        for name in self._book.sheet_names():
            sheet = self._book.sheet_by_name(name)
            #name = name.encode(self.encoding)
            dat[self.trimedValue(name)] = self.loadSheetData(sheet)
        return dat
        
    def findDataRange(self,sheet,pos,maxr):
        x,y = pos
        j = y + 1
        while j < sheet.ncols:
            if isEmptyCell(sheet.cell(x,j)) or self.isCommentCell(sheet.cell(x,y)):
                maxy = j
                break
            j += 1
        i = x + 1
        maxx = maxr
        while i < maxr:
            if not isEmptyCell(sheet.cell(i,y)):
                maxx = i
                break
            i += 1 
        return maxx
        
    def loadSheetData(self,sheet):
        return self.loadSheetDataRange(sheet,(self.startrow,self.startcol),sheet.nrows)
    
    def include(self,filename,id):
        try:
            sub = ExcelData(filename,self.encoding)
        except Exception as e:
            print(e,filename)
            return None
        if id is None:
            return sub.dict()
        env = {'data':sub.dict()}
        try:
            exec("""resutl__ = data%s""" % id,globals(),env)
        except Exception as e:
            print(e,id)
            return None
        return env['resutl__'] 
        
    def loadSingleData(self,sheet,pos):
        x,y = pos
        if sheet.ncols==y:
            v = self.cellvalue(sheet,x,y)
            if isCommentValue(v):
                return None
            return v
        ret = []
        while y < sheet.ncols:
            v = self.cellvalue(sheet,x,y)
            if v is None:
                break
            if isCommentValue(v):
                break
            ret.append(v)
            y += 1

        if len(ret) < 1:
            return None
            
        if len(ret)<2:
            return ret[0]
        if ret[0] == '__include__':
            if len(ret)<2:
                print("include mode error: __include__ filename id")
                return None
            id = None
            if len(ret)>=3:
                id = ret[2]
            return self.include(ret[1],id)
        return ret
        
    def loadDictData(self,sheet,pos,maxr):
        ret = {}
        x,y = pos
        while x < maxr:
            mr = self.findDataRange(sheet,(x,y),maxr)
            #print "loadDictData:debug:",x,y,maxr,mr
            k = self.cellvalue(sheet,x,y)
            if isCommentValue(k):
                x = x + 1
                continue
            if k is not None:
                if 'records' in k.split(':'):
                    v = self.loadRecords(sheet,(x,y+1),maxr)
                else:
                    v = self.loadSheetDataRange(sheet,(x,y+1),mr)
                ret[purekey(k)] = castedValue(v,k)
            x = mr
            
        return ret
        
    def loadSheetDataRange(self,sheet,pos,maxr):
        x,y = pos
        #print "debug1:",pos,maxr
        if maxr - x < 1 :
            #print "debug1-1:",pos,maxr
            return None
        if isEmptyCell(sheet.cell(x,y)):
            #print "debug1-2:",pos,maxr
            return None
        
        cv = self.cellvalue(sheet,x,y)
        #print cv
        if isCommentValue(cv):
            pos = (x+1,y)
            return self.loadSheetDataRange(sheet,pos,maxr)
            
        if cv == '__include__':
            return self.include(self.cellvalue(sheet,x,y+1),self.cellvalue(sheet,x,y+2))
            
        if cv == '__dict__':
            #print "cv==__dict__"
            i = x + 1
            vs = []
            while i < maxr:
                v = self.cellvalue(sheet,i,y)
                if v == '__dict__':
                    vs.append(self.loadDictData(sheet,(x+1,y),i))
                    x = i
                i += 1
            vs.append(self.loadDictData(sheet,(x+1,y),i))
            if len(vs) < 1:
                return None
            if len(vs) < 2:
                return vs[0]
            return vs
            return self.loadDictData(sheet,(x+1,y),maxr)
            
        if cv == '__list__':
            i = x + 1
            vs = []
            while i < maxr:
                v = self.loadSingleData(sheet,(i,y))
                vs.append(v)
                i += 1
            return vs
            
        if maxr - x < 2:
            v = self.loadSingleData(sheet,(x,y))
            return v
            
        return self.loadRecords(sheet,pos,maxr)
    
    def loadRecords(self,sheet,pos,maxr):
        x,y = pos
        v = self.cellvalue(sheet,x,y)
        if v==None or isCommentValue(v):
            return self.loadRecords(sheet,(x+1,y),maxr)
            
        data = []
        i = x + 1
        j = y
        keys = [ self.trimedValue(k.value) for k in sheet.row(x)[y:] ]
        while i < maxr:
            d = {}
            j = y
            while j < sheet.ncols:
                k = self.cellvalue(sheet,x,j)
                if k is None or isCommentValue(k):
                    break
                if sheet.cell_type(x,j) == xlrd.XL_CELL_EMPTY:
                    break
                v = self.cellvalue(sheet,i,j)
                if sheet.cell_type(x,j) != xlrd.XL_CELL_EMPTY:
                    d[purekey(k)] = castedValue(v,k)
                j += 1
            data.append(d)
            i += 1
        return data
        
    def dict(self):
        return self._dataset

class ExcelDataL(ExcelData):
    def dataload(self):
        ret = []
        for name in self._book.sheet_names():
            dat = {}
            sheet = self._book.sheet_by_name(name)
            name = name.encode(self.encoding)
            dat[name] = self.loadSheetData(sheet)
            ret.append(dat)
        return ret
    
if __name__ == '__main__':
    if len(sys.argv)<2:
        print("Usage:\n%s execlfile" % sys.argv[0])
        sys.exit(1)
    ed = ExcelData(sys.argv[1])
    print(ed.dict())
