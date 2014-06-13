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

import pUtils
import unittest
import tempfile
import os
from datetime import datetime, timedelta

class Test_stringToDateTime(unittest.TestCase):
    
    def setUp(self):
        pass
            
    def test_stringToDateTime_1(self):
        self.assertEqual(pUtils.stringToDateTime('2012-10-01 10:15:09'),
                                        datetime( 2012,10, 1,10,15, 9))
    
    def test_stringToDateTime_2(self):
        self.assertEqual(pUtils.stringToDateTime('20121001-011509'),
                                        datetime( 2012,10,1, 1,15, 9))
        
    def test_stringToDateTime_3(self):
        self.assertEqual(pUtils.stringToDateTime(u'2012-10-01 10:15:09'),
                                        datetime(  2012,10, 1,10,15, 9))
    
    def test_stringToDateTime_4(self):
        self.assertEqual(pUtils.stringToDateTime(u'20121001-011509'),
                                        datetime(  2012,10,1, 1,15, 9))
    
    def test_stringToDateTime_5(self):
        self.assertRaises(Exception,pUtils.stringToDateTime,'20121001-991509')
             
    def test_stringToDateTime_6(self):
        self.assertRaises(Exception,pUtils.stringToDateTime,u'2012001-xx101000')    

class Test_calculateDuration(unittest.TestCase):

    def setUp(self):
       pass

    def test_calculateDuration_1(self):
        self.assertEqual(pUtils.calculateDuration('2012-10-01 10:10:00','2012-10-02 10:10:00'),
                         timedelta(days=1))
    
    def test_calculateDuration_2(self):
        self.assertEqual(pUtils.calculateDuration('2012-10-03 10:10:00','2012-10-02 10:10:00'),
                         timedelta(days=-1))
    
    def test_calculateDuration_3(self):
        self.assertEqual(pUtils.calculateDuration('2012-10-01 10:10:00','20121001-101000'),
                         timedelta(days=0))
        
    def test_calculateDuration_4(self):
        self.assertEqual(pUtils.calculateDuration('2012-10-01 10:10:00',datetime(2012,10,01)),
                         timedelta(hours=-10,minutes=-10))
    
    #def test_calculateDuration_5(self):
    #    self.assertEqual(pUtils.calculateDuration('2012-10-01 10:10:00',u'20121001-101000'),
    #                     timedelta(days=-1))

class Test_getTimeStamp(unittest.TestCase):
    
    def setUp(self):
       pass

    #Just verify that is doesn't crash with all the valid input parameters
    #Maybe at a later time, implement the logic to verify the return value
    #with the current time +/- delta comparison. although not
    #very cost effective :P
    def test_getTimeStamp_1(self):
        pUtils.getTimeStamp()
        pUtils.getTimeStamp(0,True)
        pUtils.getTimeStamp(0,False)
        pUtils.getTimeStamp(1,True)
        pUtils.getTimeStamp(1,False)
        

        
class Test_fileOperations(unittest.TestCase):
    
    def setUp(self):
       pass

    #TODO: Break this chunk into separated tests with setUp() and tearDown()
    #TODO: quickRead/Write cases for binary, and for text specifying the parameter (instead of default)
    def test_fileOperations_1(self):
        testDirFullPath = tempfile.mkdtemp('','unitTest_pUtils_')
        self.assertEqual(os.path.exists(testDirFullPath),True)
            
        string = 'print \'Hello World!\''
        pUtils.quickFileWrite(os.path.join(testDirFullPath,'hw.py'),string)
        data = pUtils.quickFileRead(os.path.join(testDirFullPath,'hw.py'))
        self.assertEqual(string,data)

        self.assertEqual(pUtils.getFileSha1(os.path.join(testDirFullPath,'hw.py')),'a849bee4b303051f907d64b6c461ee6c699c3e79')
        
        pUtils.pSlice(os.path.join(testDirFullPath,'hw.py'),1)
        self.assertEqual(len(pUtils.filterListByRegex(os.listdir(testDirFullPath),r'hw\.py\.[0-9]+')),21)
        os.remove(os.path.join(testDirFullPath,'hw.py'))
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'hw.py')),False)
        pUtils.pUnSlice(os.path.join(testDirFullPath,'hw.py.0'))
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'hw.py')),True)
        self.assertEqual(pUtils.quickFileRead(os.path.join(testDirFullPath,'hw.py')),string)
        
        pUtils.createZipFile(testDirFullPath,['hw.py'],os.path.join(testDirFullPath,'aFile.zip'))
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'aFile.zip')),True)
        os.remove(os.path.join(testDirFullPath,'hw.py'))
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'hw.py')),False)
        pUtils.unzipFile(os.path.join(testDirFullPath,'aFile.zip'),testDirFullPath)
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'hw.py')),True)
        self.assertEqual(pUtils.quickFileRead(os.path.join(testDirFullPath,'hw.py')),string)
        
        pUtils.emptyDirectory(testDirFullPath)
        self.assertEqual(len(os.listdir(testDirFullPath)),0)
        
        pUtils.createDirectory(os.path.join(testDirFullPath,'ttt','ttt2'))
        self.assertEqual(os.path.exists(os.path.join(testDirFullPath,'ttt','ttt2')),True)
        
        pUtils.removeDirectory(testDirFullPath)
        self.assertEqual(os.path.exists(testDirFullPath),False)
        

class Test_packingFunctions(unittest.TestCase):
    
    def setUp(self):
       pass

    def test_packingFunctions_1(self):
        data = 'I am a random string to be used for this test!'
        self.assertEqual(pUtils.pUnpack(pUtils.pPack(data)),data)


#TODO increase coverage by adding run programs (instead of only shell commands) cases
class Test_runProgram(unittest.TestCase):

    def setUp(self):
       pass

    def test_runProgram_1(self):
        t = pUtils.runProgram('ls',shell=True)
        t['output']
        t['errorCode']
        self.assertEqual(t['returnCode'],0)
       
class Test_removeDuplicates(unittest.TestCase):

    def test_removeDuplicates_1(self):
        self.assertEqual(pUtils.removeDuplicates([1,2,3,4,2,3,3]),[1,2,3,4])

class Test_removeEntries(unittest.TestCase):

    def test_removeEntries_1(self):
        self.assertEqual(pUtils.removeEntries([1,2,2,3,5],[2,3]),[1,5])

class Test_filterListByRegex(unittest.TestCase):

    def test_filterListByRegex_1(self):
        self.assertEqual(pUtils.filterListByRegex(['abc','etc','abd'],r'.?.?c'),['abc','etc'])

class Test_replaceStrings(unittest.TestCase):

    def test_replaceStrings_1(self):
        d = {'<w1>':'World','<w2>':'again'}
        self.assertEqual(pUtils.replaceStrings('Hello <w1> ! ... <w2> and <w2>',**d),'Hello World ! ... again and again')

class Test_formatHex(unittest.TestCase):

    def test_Test_formatHex_1(self):
        data = bytearray('\x00\x01\x02\x03\xFF')
        self.assertEqual(pUtils.formatHex(data),'00 01 02 03 FF')

    def test_Test_formatHex_2(self):
        data = '\x00\x01\x02\x03\xFF'
        self.assertEqual(pUtils.formatHex(data),'00 01 02 03 FF')




if __name__ == '__main__':
    import inspect
    import sys
    itemList = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    
    suiteList = []
    for item in itemList:
        suiteList.append(unittest.TestLoader().loadTestsFromTestCase(item[1]))
    allTests = unittest.TestSuite(suiteList)
    unittest.TextTestRunner(verbosity=2).run(allTests)
 
