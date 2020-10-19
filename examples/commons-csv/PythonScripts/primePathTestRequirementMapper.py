import os,sys
import json
from collections import defaultdict
from pprint import pprint


#INPUT FILE:
# 1. <sourceClass>-CFGprimeCoverageRequirements.txt
# 2. <sourceClass>-CFGmapping.json
# 3. <sourceClass>-StatementsCovered.txt
# 4. output directory

#OUTPUT:
# <sourceClass>-SmartTestData.json

def convertJsonToDict(jsonMapping):
    mappingDict = dict()
    for data in jsonMapping:
        for k,v in data.items():
            mappingDict[k]=v
    return mappingDict

def generateRequirementToLineNumberMapping(mapping, primePathRequirements, requirementList):
    mappingData = json.load(mapping)
    mappingDict = convertJsonToDict(mappingData)
    requirements=[]
    counter=1
    for line in primePathRequirements:
        newline=""
        for node in line.strip().split(","):
            if node and node in mappingDict:
                lineNumber = mappingDict[node]['line']
                if(lineNumber):
                    if(newline):
                        newline=newline+","+str(lineNumber)
                    else:
                        newline=str(lineNumber)
        requirements.append(newline)
        testRequirement = "TR"+str(counter)
        counter+=1
        requirementList[testRequirement]=newline


def generateTestToSatisfiedRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList):
    for line in statementCoverageInfo:
        satisfiedRequirement=[]

        if "=" in line:
            testName= line.split(" : ")[0]
            coverageInfo = line.split(" : ")[1]
            for methods in coverageInfo.split(";"):
                statements = methods.split("=")[1].strip()
                print(requirementList.items(),"-------------------")
                print(statements)
                req = [key  for (key, value) in requirementList.items() if value in statements]
                print(req)
                break
                for r in req:
                    if r not in satisfiedRequirement:
                        satisfiedRequirement.append(r)
            break
            testAndRequirementSatisfied[testName]=satisfiedRequirement



def dumpTestInfo(baseDir,requirementList,testAndRequirementSatisfied,sourceFileName):
    pathToOutputFolder = os.path.dirname(baseDir)
    versionInformation = dict()
    requirementsInformation = dict ()
    testInformation = dict ()

    versionInformation['info']=baseDir.split(os.path.sep)[-1]
    requirementsInformation['requirements'] = requirementList
    testInformation['testCoverage'] = testAndRequirementSatisfied



    todump=[]
    todump.append(versionInformation)
    todump.append(requirementsInformation)
    todump.append(testInformation)
    outputJsonFile = sourceFileName+'-primePathTracker.json'
    with open(pathToOutputFolder+os.path.sep+outputJsonFile, 'w') as mappingFile:
        json.dump(todump,mappingFile,indent=2)




def main():
    if(len(sys.argv)>1):
        folderName = sys.argv[-2]
        sourceFileName = sys.argv[-1]
        primePathFileName=sourceFileName+"-primePathCoverageRequirements.txt"
        mappingFile =sourceFileName+"-CFGmapping.json"
        statementCoverageFile = sourceFileName+"-StatementsCovered.txt"
    else:
        print('Usage: python3 primePathTestRequirementMapper.py ../output/<subDirVersion> <sourceClass> \nNeeds you to run <mvn verify> from project dir first')
        return

    baseDir = os.path.abspath(folderName)  #complete current analysis directory like .../.../27-04-2020_17:01:08
    pathToOutputFolder = os.path.dirname(baseDir)

    primePathRequirements = open(baseDir+os.path.sep+primePathFileName,'r')
    statementCoverageInfo = open (pathToOutputFolder+os.path.sep+statementCoverageFile,'r')
    mapping = open(baseDir+os.path.sep+mappingFile,'r')

    requirementList=dict()

    generateRequirementToLineNumberMapping(mapping, primePathRequirements, requirementList)

    testAndRequirementSatisfied =  dict()

    generateTestToSatisfiedRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList)


    dumpTestInfo(baseDir,requirementList,testAndRequirementSatisfied,sourceFileName)








if __name__=='__main__':
    main()
