import xlwt
from appPublic.strUtils import *

class ExcelWriter:
    def __init__(self,encoding='gb2312'):
        self.encoding = encoding
        
    def writeV(self,sheet,x,y,v):
        if type(v) == type([]):
            return self.writeList(sheet,x,y,v)
        
        if type(v) == type({}):
            return self.writeDict(sheet,x,y,v)
        
        if type(v) not in (type({}),type([])):
            if type(v) == type(' '):
                v = lrtrim(v)
            sheet.write(x,y,v)
            return 1
                
    def write(self,excelfile,dictdata):
        wb = xlwt.Workbook(encoding=self.encoding)
        for tbl in dictdata.keys():
            ws = wb.add_sheet(tbl,cell_overwrite_ok=True)
            self.writeV(ws,0,0,dictdata[tbl])
        wb.save(excelfile)
    
    def createRecordTitle(self,ws,x,y,title,poss,isList=False):
        if isList:
            poss['__list__'][title] = True

        if title in poss.keys():
            return
        
        if len(poss.keys()) > 1:
            d_ = {}
            for k,v in poss.items():
                if k != '__list__':
                    d_[k] = v
            y = max(d_.values()) + 1
        # ws.write(x,y,title)
        poss[title] = y
    
    def writeRecordTitle(self,ws,x,poss):
        for k in poss.keys():
            if k == '__list__':
                continue
            if k in poss['__list__'].keys():
                ws.write(x,poss[k],k+':list')
            else:
                ws.write(x,poss[k],k)
           
    def writeRecords(self,ws,x,y,alist):
        ox = x
        oy = y
        poss = {'__list__':{}}
        x = ox + 1
        for r in alist:
            for k,v in r.items():
                isList = False
                if type(v) == type([]):
                    isList = True
                    v = ','.join(v)
                self.createRecordTitle(ws,ox,oy,k,poss,isList)
                ws.write(x,poss[k],v)
            x = x + 1
        self.writeRecordTitle(ws,ox,poss)
        return x - ox

    def isRecords(self,alist):
        records = True
        for r in alist:
            if type(r) != type({}):
                return False
            for k,v in r.items():
                if type(v) == type({}):
                    return False
                if type(v) == type([]):
                    for c in v:
                        if type(c) in [type([]),type({})]:
                            return False
        return True
        
    def writeDict(self,ws,x,y,adict):
        ox = x
        ws.write(x,y,'__dict__')
        x = x + 1
        for k in adict.keys():
            ws.write(x,y,k)
            cnt = self.writeV(ws,x,y+1,adict[k])
            x = x + cnt
            # print "writeV return ",cnt,"handled key=",k,"next row=",x
        return x - ox
     
    def writeList(self,ws,x,y,alist,singlecell=False):
        if self.isRecords(alist):
            return self.writeRecords(ws,x,y,alist)
            
        ox = x
        if singlecell is True:
            s = ','.join([ str(i) for i in alist ])
            ws.write(x,y,s)
            return 1
        multiline = False
        for d in alist:
            if type(d) == type({}):
                multiline=True
        if multiline is True:
            for i in alist:
                if type(i) == type({}):
                    rows = self.writeDict(ws,x,y,i)
                elif type(i) == type([]):
                    rows = self.writeMultiLineList(ws,x,y,i)
                else:
                    ws.write(x,y,i)
                    rows = 1
                x = x + rows
            return x - ox
        else:
            for i in alist:
                if type(i) == type([]):
                    self.writeList(ws,x,y,i,singlecell=True)
                else:
                    ws.write(x,y,i)
                y = y + 1
            return 1

    def writeMultiLineList(self,ws,x,y,alist):
        ox = x
        ws.write(x,y,'__list__')
        x = x + 1
        for i in alist:
            ws.write(x,y,i)
            x = x + 1
        return x - os

if __name__ == '__main__':
    data = {
        'my1':['23423','423424','t334t3',2332,'erfverfefew'],
        'my2':[{'aaa':1,'bbb':'bbb'},{'aaa':1,'bbb':'bbb'}],
    }
    w = ExcelWriter()
    w.write('d:\\text.xls',data)
       