import os
import json
import subprocess
import re
import zipfile
import hashlib
from datetime import datetime

def quickFileRead(fileFullPath,mode='rt'):
    with open(fileFullPath,mode) as file:
        data = file.read()
    return data

def quickFileWrite(fileFullPath,data,mode='wt'):
    dir = os.path.dirname(fileFullPath)
    if dir!='': createDirectory(dir)
    with open(fileFullPath,mode) as file:
        file.write(data)

def dateTimeToString(dateTimeObj,formatTypeID=0):
    if formatTypeID==0:
        t = dateTimeObj
        s = t.date().isoformat().replace('-','')+'-'+t.time().isoformat().replace(':','')
        s = s[:15]
        return s
    if formatTypeID==1:
        return str(dateTimeObj).split('.')[0]
    
def stringToDateTime(string):
    patternList = [
        '%Y%m%d-%H%M%S',
        '%Y-%m-%d %H:%M:%S'
    ]
    for pattern in patternList:
        try:
            obj = datetime.strptime(string,pattern)
            return obj
        except:
            pass
    raise Exception('Unrecognized dateTime format: '+string)
    
def getTimeStamp(formatTypeID=0,utc=True):
    if utc:
        t = datetime.utcnow()
    else:
        t = datetime.now()
    return dateTimeToString(t,formatTypeID)

def calculateDuration(start,end):
    if isinstance(start,str):
        start = stringToDateTime(start)
    if isinstance(end,str):
        end = stringToDateTime(end)
    delta = end - start
    return delta

def runProgram(programFullPath,shell=False):
    s = subprocess.Popen(programFullPath, stdout=subprocess.PIPE,shell=shell)
    output, errorCode = s.communicate()
    returnCode = s.returncode
    return {'output':output,'errorCode':errorCode,'returnCode':returnCode}

def getFileSha1(fileNameFullPath):
    sha1Obj = hashlib.sha1()
    sha1Obj.update(quickFileRead(fileNameFullPath,'rb'))
    hexStringSha1 = sha1Obj.hexdigest()   
    return hexStringSha1

def pSlice(inFileNameFullPath,sliceSize):
    base = inFileNameFullPath
    counter = 0
    with open(inFileNameFullPath,'rb') as inFile:
        while True:
            data = inFile.read(sliceSize)
            if not data: break
            counter += 1
            quickFileWrite(base+'.'+str(counter),data,'wb')
    referenceData = {}
    referenceData['sliceAmount'] = counter
    quickFileWrite(base+'.'+'0',json.dumps(referenceData))
    return counter

def pUnSlice(inFileNameFullPath):
    base = '.'.join(inFileNameFullPath.split('.')[:-1])
    referenceData = json.loads(quickFileRead(base+'.0'))
    sliceAmount = referenceData['sliceAmount']
    with open (base,'wb') as outFile:
        for i in range(1,sliceAmount+1):
            data = quickFileRead(base+'.'+str(i),'rb')
            outFile.write(data)

def createZipFile(rootPath,inFileRelativePathList,outFileNameFullPath):
    theZipFile = zipfile.ZipFile(outFileNameFullPath,'w',zipfile.ZIP_DEFLATED)
    
    for inFileRelativePath in inFileRelativePathList:
        inFileFullPath = os.path.join(rootPath,inFileRelativePath)
        theZipFile.write(inFileFullPath,inFileRelativePath)
    
    theZipFile.close()
    return outFileNameFullPath

def unzipFile(inFileFullPath,outDirFullPath):
    theZip = zipfile.ZipFile(inFileFullPath,'r')
    
    fileNameZipPathList=theZip.namelist()
    for fileNameZipPath in fileNameZipPathList:
        path = os.path.join(outDirFullPath,fileNameZipPath)
        if fileNameZipPath[-1]=='/' :
            createDirectory(path)
        else:
            quickFileWrite(path,theZip.read(fileNameZipPath),'wb')
    theZip.close()
    return 0

def createDirectory(path):
    if os.path.exists(path)!=True:
        os.makedirs(path)
        return 0
    else:
        return 1

def removeDirectory(path):
    list = os.listdir(path)
    list = map(lambda s:os.path.join(path,s),list)
    for item in list:
        if os.path.isfile(item):
            os.remove(item)
        else:
            removeDirectory(item)
    os.rmdir(path)

def emptyDirectory(path):
    list = os.listdir(path)
    list = map(lambda s:os.path.join(path,s),list)
    for item in list:
        if os.path.isfile(item):
            os.remove(item)
        else:
            removeDirectory(item)

def removeDuplicates(list):
    list.sort()
    list2 = []
    old=''
    for l in list:
        if old!=l:
            list2 = list2 +[l]
            old=l
    return list2

def removeEntries(mainList,removeList):
    l=[]
    for mainItem in mainList:
            if mainItem not in removeList:
                l.append(mainItem)
    return l

def filterListByRegex(list, regex):
    list2 = []
    r = re.compile(regex)
    for item in list:
        t = r.search(item)
        if t!=None:
            list2.append(item)
    return list2
    
def replaceStrings(string,**kwargs):
    for i,j in kwargs.iteritems():
        string = string.replace(i,j)
    return string