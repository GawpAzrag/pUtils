#Copyright (c) 2012, Pablo De La Garza
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#-Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
#-Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#POSSIBILITY OF SUCH DAMAGE.

import os
import json
import subprocess
import re
import zipfile
import zlib
import base64
import hashlib
from datetime import datetime

def quickFileRead(fileFullPath,mode='rt'):

    modeTmp = mode

    if (mode=='json' or 
        mode=='csv' or
        mode=='txt'):

        modeTmp = 'rt'

    with open(fileFullPath,modeTmp) as inFile:
        data = inFile.read()

    if mode=='json':
        data = json.loads(data)
    elif mode=='csv':
        data = [row.split(',') for row in data.split('\n') if row!=''] 
    elif mode=='txt':
        data = [item for item in data.split('\n') if item!='']
    
    return data

def quickFileWrite(fileFullPath,data,mode='wt'):
    dirFullPath = os.path.dirname(fileFullPath)
    createDirectory(dirFullPath)

    if mode=='json':
        data = json.dumps(data,indent=4,sort_keys=True)
        mode = 'wt'
    elif mode=='csv':
        data = '\n'.join([','.join([str(item) for item in row]) for row in data])
        mode = 'wt'
    elif mode=='txt':
        data = '\n'.join([str(item) for item in data])
        mode = 'wt'
    
    with open(fileFullPath,mode) as outFile:
        outFile.write(data)

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
    s = subprocess.Popen(programFullPath, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=shell)
    output, errorCode = s.communicate()
    returnCode = s.returncode
    return {'output':output,'errorCode':errorCode,'returnCode':returnCode}

def getFileSha1(fileNameFullPath):
    sha1Obj = hashlib.sha1()
    sha1Obj.update(quickFileRead(fileNameFullPath,'rb'))
    hexStringSha1 = sha1Obj.hexdigest()   
    return hexStringSha1

def pSlice(inFileFullPath,outDirectoryFullPath,sliceSize):
    
    referenceData = {}
    checksumDict = {}
    referenceData['checksumDict'] = checksumDict
    
    fileName = os.path.basename(inFileFullPath)
    
    checksumDict[fileName] = getFileSha1(inFileFullPath)
    
    counter = 0
    with open(inFileFullPath,'rb') as inFile:
        while True:
            data = inFile.read(sliceSize)
            if not data: break
            counter += 1
            fileFullPath = os.path.join(outDirectoryFullPath,fileName+'.'+str(counter))
            quickFileWrite(fileFullPath,data,'wb')
            checksumDict[os.path.basename(fileFullPath)] = getFileSha1(fileFullPath)
            
    referenceData['sliceAmount'] = counter
    fileFullPath = os.path.join(outDirectoryFullPath,fileName+'.'+'0')
    quickFileWrite(fileFullPath,json.dumps(referenceData))
    
    return {'retCode':0,'errMsg':None}


def pUnSlice(inFileFullPath,outFileFullPath):
    base = '.'.join(inFileFullPath.split('.')[:-1])
    referenceData = json.loads(quickFileRead(base+'.0'))
    sliceAmount = referenceData['sliceAmount']
    
    createDirectory(os.path.dirname(outFileFullPath))
    with open (outFileFullPath,'wb') as outFile:
        for i in range(1,sliceAmount+1):
            data = quickFileRead(base+'.'+str(i),'rb')
            outFile.write(data)
    
    if getFileSha1(outFileFullPath)!=referenceData['checksumDict'][os.path.basename(inFileFullPath[:-2])]:
        return {'retCode':1,'errMsg':'Checksum for whole file failed'}
    
    return {'retCode':0,'errMsg':None}
    

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

def pPack(data):
    return base64.b64encode(zlib.compress(data))

def pUnpack(package):
    return zlib.decompress(base64.b64decode(package))

def createDirectory(path):
    if path=='': return 2
    if os.path.exists(path)!=True:
        os.makedirs(path)
        return 0
    else:
        return 1

def removeDirectory(path):
    itemList = os.listdir(path)
    itemList = map(lambda s:os.path.join(path,s),itemList)
    for item in itemList:
        if os.path.isfile(item):
            os.remove(item)
        else:
            removeDirectory(item)
    os.rmdir(path)

def emptyDirectory(path):
    itemList = os.listdir(path)
    itemList = map(lambda s:os.path.join(path,s),itemList)
    for item in itemList:
        if os.path.isfile(item):
            os.remove(item)
        else:
            removeDirectory(item)

def removeDuplicates(itemList):
    itemList.sort()
    itemList2 = []
    old=''
    for l in itemList:
        if old!=l:
            itemList2 = itemList2 +[l]
            old=l
    return itemList2

def removeEntries(mainList,removeList):
    l=[]
    for mainItem in mainList:
            if mainItem not in removeList:
                l.append(mainItem)
    return l

def filterListByRegex(itemList, regex):
    itemList2 = []
    r = re.compile(regex)
    for item in itemList:
        t = r.search(item)
        if t!=None:
            itemList2.append(item)
    return itemList2
    
def replaceStrings(string,**kwargs):
    for i,j in kwargs.iteritems():
        string = string.replace(i,j)
    return string

def formatHex(data):
    data = bytearray(data)
    return ' '.join(['%02X' % byte for byte in data])


