import sys, os
import json
from collections import defaultdict
from difflib import SequenceMatcher
import subprocess
import itertools

class Verifier:
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

def main():
    if(len(sys.argv)>1):
        changedLine = sys.argv[-1]
        outputDataFileName = sys.argv[-2]
        verifier = Verifier()
    else:
        print('Example: python3 verifier.py FiniteDifferencesDifferentiator-02-09-2020_19_14_05.json 256')
        print('Usage: python3 verifier.py <outputDataFileName with json> <changedLine>')
        return

    sourceBeingVerified = outputDataFileName.split("-")[0]
    outputDataLocation="../finalResult"
    outputData = verifier.getRelevantData(outputDataLocation,outputDataFileName)
    # print(outputData)
    baseDataFileName = outputDataFileName.split("-")[0]
    baseDataLocation="../Original"
    baseDataJson = verifier.getRelevantData(baseDataLocation,baseDataFileName+"-SmartTestData.json")
    baseData = verifier.convertJsonToDict(baseDataJson)
    # print(baseData)
    exactMatch = False
    if "sourceCodeStatus" in outputData:
        changeInFile = outputData.get("sourceCodeStatus").get("sourceClass") #compare with baseDataFileName
    else:
        print("Final result file was empty")
        return

    if changeInFile == baseDataFileName:
        changeDetectedLine = outputData.get("sourceCodeStatus").get("line") #compare with changedLine

        # print(changeDetectedLine)
        # print(changedLine)
        if changedLine == changeDetectedLine[0]:
            exactMatch = True
        if changedLine in changeDetectedLine:
            testCodeStatus = outputData.get("testCodeStatus")

            affectedReqReported = testCodeStatus.get("affectedReq")
            startOfChangedLine = changedLine+","
            endOfChangedLine = ","+changedLine
            affectedRequirements= [key  for key, value in baseData['requirements'].items() if value.startswith(startOfChangedLine) or value.endswith(endOfChangedLine) ]
            if affectedReqReported and affectedRequirements:
                if sorted(affectedReqReported) == sorted(affectedRequirements) and exactMatch:
                    affectedTestReported = testCodeStatus.get("affectedTest")
                    testReranReported = testCodeStatus.get("testReran")
                    affectedTest = set([key for affectedRequirement in affectedRequirements for key, value in baseData['testCoverage'].items() if affectedRequirement in value ])
                    if affectedTestReported and affectedTest:
                        if (sorted(affectedTestReported) == sorted(affectedTest) and exactMatch) or (all (item in affectedTest for item in affectedTestReported) and not exactMatch):
                            if all(item in testReranReported for item in affectedTest):
                                print("VERIFICATION DONE==========="+outputDataFileName+" is good")
                            else:
                                print(outputDataFileName)
                                print("test reran didn't match")
                        else:
                            print(outputDataFileName)
                            print("Affected test didn't match")
                    else:
                        if not affectedTestReported and not affectedTest:
                            print(outputDataFileName,"------- No test affected or reported. Matches")
                        else:
                            if not affectedTestReported:
                                print(outputDataFileName,"------- No affected test reported")
                            if not affectedTest:
                                print(outputDataFileName,"------- No test affected")
                elif all(item in affectedRequirements for item in affectedReqReported):
                    affectedTestReported = testCodeStatus.get("affectedTest")
                    testReranReported = testCodeStatus.get("testReran")
                    affectedTest = set([key for affectedRequirement in affectedRequirements for key, value in baseData['testCoverage'].items() if affectedRequirement in value ])
                    if affectedTestReported and affectedTest:
                        if (sorted(affectedTestReported) == sorted(affectedTest) and exactMatch) or (all (item in affectedTest for item in affectedTestReported) and not exactMatch):
                            if all(item in testReranReported for item in affectedTest):
                                print("VERIFICATION DONE==========="+outputDataFileName+" is good but extra lines flagged")
                            else:
                                print(outputDataFileName)
                                print("test reran didn't match")
                        else:
                            print(outputDataFileName)
                            print("Affected test didn't match")
                    else:
                        if not affectedTestReported and not affectedTest:
                            print(outputDataFileName,"------- No test affected or reported. Matches")
                        else:
                            if not affectedTestReported:
                                print(outputDataFileName,"------- No affected test reported")
                            if not affectedTest:
                                print(outputDataFileName,"------- No test affected")
                else:
                    print(outputDataFileName,"------------ Affected requirement didn't match")
            else:
                if not affectedReqReported and not affectedRequirements:
                    print(outputDataFileName,"------- No requirements affected or reported. Matches")
                else:
                    if not affectedReqReported:
                        print("No affected requirement reported")
                    if not affectedRequirements:
                        print("No requirements affected")
        else:
            print(outputDataFileName,"------- Line didn't match")
    else:
        print(outputDataFileName,"------- File didn't match")











if __name__=='__main__':
    main()
