import os,sys
import json
from collections import defaultdict
from pprint import pprint

def convertJsonToDict(jsonMapping):
    mappingDict = dict()
    for data in jsonMapping:
        for k,v in data.items():
            mappingDict[k]=v
    return mappingDict

def analyzeTestRequirements(mapping, edgePathRequirements, requirementList):
    mappingData = json.load(mapping)
    mappingDict = convertJsonToDict(mappingData)
    requirements=[]
    counter=1
    for line in edgePathRequirements:
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


def generateTestRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList):

    for line in statementCoverageInfo:
        satisfiedRequirement=[]

        if "=" in line:
            testName= line.split(" : ")[0]
            coverageInfo = line.split(" : ")[1]
            for methods in coverageInfo.split(";"):
                statements = methods.split("=")[1].strip()
                req = [key  for (key, value) in requirementList.items() if value in statements]
                for r in req:
                    if r not in satisfiedRequirement:
                        satisfiedRequirement.append(r)
            print(satisfiedRequirement)
            #ßsatisfiedRequirementSet=list(satisfiedRequirement)
            testAndRequirementSatisfied[testName]=satisfiedRequirement



def dumpTestInfo(baseDir,requirementList,testAndRequirementSatisfied):
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
    # pprint(todump)
    with open(pathToOutputFolder+os.path.sep+'SmartTestData.json', 'w') as mappingFile:
        json.dump(todump,mappingFile,indent=2)




def main():
    if(len(sys.argv)>1):
        folderName=sys.argv[-3]
        edgePathFileName=sys.argv[-2]
        mappingFile = sys.argv[-1]
    else:
        print('Usage: python3 finalAnalysis.py ../output/<subDirVersion> <sourceClass>-CFGedgeCoverageRequirements.txt <sourceClass>-CFGmapping.json \nNeeds you to run <mvn verify> from project dir first')
        return

    baseDir = os.path.abspath(folderName)  #complete current analysis directory like .../.../27-04-2020_17:01:08

    print(baseDir)


    edgePathRequirements = open(baseDir+os.path.sep+edgePathFileName,'r')

    pathToOutputFolder = os.path.dirname(baseDir)
    print(pathToOutputFolder)
    statementCoverageInfo = open (pathToOutputFolder+os.path.sep+'StatementsCovered.txt','r')


    mapping = open(baseDir+os.path.sep+mappingFile,'r')

    requirementList=dict()

    analyzeTestRequirements(mapping, edgePathRequirements, requirementList)
    # print(requirementList)

    testAndRequirementSatisfied =  dict()

    generateTestRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList)


    dumpTestInfo(baseDir,requirementList,testAndRequirementSatisfied)








if __name__=='__main__':
    main()
