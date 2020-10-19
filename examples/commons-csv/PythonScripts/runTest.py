import sys, os
import json
from collections import defaultdict
from difflib import SequenceMatcher
import subprocess
import itertools

class RerunTest:
    def __init__(self):
        self.recordWork=''

    def convertJsonToDict(self,jsonMapping):
        mappingDict = dict()
        for data in jsonMapping:
            for k,v in data.items():
                mappingDict[k]=v
        return mappingDict

    def getRelevantData(self,fileDir,fileName):
        file = os.path.join(os.path.abspath(fileDir),fileName)

        fileContentStream = open(file,'r')
        fileContent = json.load(fileContentStream)

        fileContentStream.close()
        return fileContent



def runTest(newVersion, mutatedSource,item,packagePath):
    r = RerunTest()



    testFileToReRun = mutatedSource+"TestIT"
    outputDataLocation="../finalResult"
    outputDataFileName = mutatedSource+"-"+newVersion+".json"
    outputData = r.getRelevantData(outputDataLocation,outputDataFileName)


    if "testCodeStatus" in outputData:
        testToReRun = outputData.get("testCodeStatus").get("testReran") #compare with baseDataFileName
        testToRemove  = outputData.get("testCodeStatus").get("deletedTest") #compare with baseDataFileName
        if testToReRun:
            for test in testToReRun:
                testRunningCommand="mvn"+" -Dtest="+mutatedSource+"TestIT#"+test+" test -q"
                try:
                    subprocess.run(testRunningCommand,shell=True, check=True)
                except subprocess.CalledProcessError:
                    print("testFailed for mutation",item)
        if testToRemove:
            '''
            finds the line number to be commented by searching for test name and comments lines between @Test testtoDelete @Test.
            writes in the actual test.java file
            '''
            testPath = packagePath.replace("main","test")
            testFile = testPath+os.path.sep+mutatedSource+"TestIT.java"
            newTestFile = testPath+os.path.sep+mutatedSource+"-Changed-TestIT.java"
            testContentStream = open(testFile,"r")
            testContent = testContentStream.readlines()
            testContentStream.close()
            linesTobeCommented= {}


            for test in testToRemove:
                startFound = False
                # print(test,"---------------------",testPath)
                for num,line in enumerate(testContent,1):
                    if test in line:
                        startComment = num-1
                        startFound = True
                    if startFound and "@Test" in line:
                        endComment = num-1
                        break
                linesTobeCommented[startComment]=(startComment,endComment)

            newTestStream = open(testFile,"w")
            commentBlockFound=False

            for num,line in enumerate(testContent,1):
                if num in linesTobeCommented.keys():
                    commentBlockFound = True
                    commentBlock = linesTobeCommented[num]
                    start = commentBlock[0]
                    endOfBlock = commentBlock[1]
                if commentBlockFound and num <= endOfBlock:
                    line = "// "+line
                    newTestStream.write(line)
                else:
                    newTestStream.write(line)
            newTestStream.close()






    else:
        print("No test to rerun")
        return












#
# if __name__=='__main__':
#     main()
