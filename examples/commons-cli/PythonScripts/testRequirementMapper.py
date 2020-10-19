import os,sys
import json
from collections import defaultdict
from pprint import pprint


#INPUT FILE:
# 1. <sourceClass>-CFGedgeCoverageRequirements.txt
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

def generateRequirementToLineNumberMapping(mapping, edgePathRequirements, requirementList):
    mappingData = json.load(mapping)
    mappingDict = convertJsonToDict(mappingData)
    requirements=[]
    edgesList=[]
    counter=1
    for line in edgePathRequirements:
        edgeMaps={}
        nodes = line.strip().split(",")
        edgeMaps[nodes[0]] = nodes[1]
        edgesList.append(edgeMaps)
    edgePathRequirements.seek(0)
    for line in edgePathRequirements:
        skipLine = False
        newline=""
        for node in line.strip().split(","):
            if node and node in mappingDict:
                lineNumber = mappingDict[node]['line']
                if(lineNumber and lineNumber!= 0):
                    if(newline):
                        newline=newline+","+str(lineNumber)
                    else:
                        newline=str(lineNumber)
                else:
                    if(newline):        #if this node is end of an edge, need to find the appropriate end
                        newLineNumber =0
                        problematicNode = node
                        while(newLineNumber==0):
                            newNode = [end for edges in edgesList for start,end in edges.items() if start==problematicNode]
                            if newNode:                             # if there is an end node to the edge but it has line number =0 then keep looking for next node
                                if newNode[0] in mappingDict:
                                    newLineNumber = mappingDict[newNode[0]]['line']
                                    problematicNode=newNode[0]
                                else:
                                    newLineNumber = 0
                                    problematicNode=newNode[0]
                            else:                                   # there is no end node to the edge, ignore requirement
                                skipLine=True
                                break
                        if not skipLine:
                            newline = newline+","+str(newLineNumber)
                    else:
                        skipLine = True
                        break
        if not skipLine:
            requirements.append(newline)
            testRequirement = "TR"+str(counter)
            counter+=1
            requirementList[testRequirement]=newline
    # print(requirementList,"------")


def generateTestToSatisfiedRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList,noRequirement):
    for line in statementCoverageInfo.split("\n\n"):
        satisfiedRequirement=[]
        if "=" in line:
            testName= line.split(" : ")[0].strip().replace("\n","")
            coverageInfo = line.split(" : ")[1]
            for methods in coverageInfo.split(";;"):
                methodName = methods.split("=")[0]
                if "<clinit>" not in methodName:
                    edges = methods.split("=")[1].strip().replace("[","").replace("\n]","")
                    edgeList=edges.split("\n")
                    for edge in edgeList:
                        req = [key for (key, value) in requirementList.items() if value == edge.strip()]
                        if(req):
                            if req not in satisfiedRequirement:
                                satisfiedRequirement.append(req[0])
                        else:
                            noRequirement[testName].add(edge.strip())
            testAndRequirementSatisfied[testName]=satisfiedRequirement

            #     for statement in statements:
            #         # print(statement,"-----")1,2,3,4,4,
            # TR1: 1,2
            #         req = [key for (key, value) in requirementList.items() if value in statement]
            #     # req = [key  for (key, value) in requirementList.items() if value in statements]
            #     # print(req)
            #     for r in req:
            #         if r not in satisfiedRequirement:
            #             satisfiedRequirement.append(r)
            # testAndRequirementSatisfied[testName]=satisfiedRequirement



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
    outputJsonFile = sourceFileName+'-SmartTestData.json'
    with open(pathToOutputFolder+os.path.sep+outputJsonFile, 'w') as mappingFile:
        json.dump(todump,mappingFile,indent=2)




def main():
    if(len(sys.argv)>1):
        folderName = sys.argv[-2]
        sourceFileName = sys.argv[-1]
        edgePathFileName=sourceFileName+"-CFGedgeCoverageRequirements.txt"
        mappingFile =sourceFileName+"-CFGmapping.json"
        statementCoverageFile = sourceFileName+"-StatementsCovered.txt"
    else:
        print('Usage: python3 testRequirementMapper.py ../output/<subDirVersion> <sourceClass> \nNeeds you to run <mvn verify> from project dir first')
        return

    baseDir = os.path.abspath(folderName)  #complete current analysis directory like .../.../27-04-2020_17:01:08
    pathToOutputFolder = os.path.dirname(baseDir)

    try:
        edgePathRequirements = open(baseDir+os.path.sep+edgePathFileName,'r')
    except OSError as e:
        print("No edge path requirement!")
        return

    statementCoverageInfo = open (pathToOutputFolder+os.path.sep+statementCoverageFile,'r').read()
    mapping = open(baseDir+os.path.sep+mappingFile,'r')

    requirementList=dict()
    noRequirement=defaultdict(set)

    generateRequirementToLineNumberMapping(mapping, edgePathRequirements, requirementList)

    testAndRequirementSatisfied =  dict()

    generateTestToSatisfiedRequirementMapping(statementCoverageInfo,testAndRequirementSatisfied,requirementList,noRequirement)


    dumpTestInfo(baseDir,requirementList,testAndRequirementSatisfied,sourceFileName)








if __name__=='__main__':
    main()
