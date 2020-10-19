import sys, os
import json
from collections import defaultdict
from difflib import SequenceMatcher
import subprocess

def convertJsonToDict(jsonMapping):
    mappingDict = dict()
    for data in jsonMapping:
        for k,v in data.items():
            mappingDict[k]=v
    return mappingDict

def allPaths(edgePathFile):  #convert path as text to list
    allPaths=[]
    for path in edgePathFile:  #from edgePath file
        path = path.strip().strip(',').split(",")
        allPaths.append(path)
    return allPaths

def getNodesByFunc(allPaths):
    nodesInFuncs = defaultdict(set)
    for path in allPaths:
        for i in path:
            nodesInFuncs[path[0]].add(i)
    return nodesInFuncs

def main():
    if(len(sys.argv)>1):
        originalVersion = sys.argv[-2]
        newVersion = sys.argv[-1]
        sourceClassName = sys.argv[-3]
        # oldPathFile=sys.argv[-1]
        # mappingOfOld=sys.argv[-2]
        # newPathFile=sys.argv[-3]
        # mappingOfNew=sys.argv[-4]

    else:
        print('python3 comparator.py SourceClass ../output/27-04-2020_17_01_08 ../output/27-04-2020_17_01_08')
        print('Usage: python3 comparator.py <SourceClassName> ../output/<originalVersionDir> ../output/<newVersionDir>')
        return

    originalVersionEdges = os.path.join(os.path.abspath(originalVersion),sourceClassName+'-CFGedgepaths.txt')
    newVersionEdges = os.path.join(os.path.abspath(newVersion),sourceClassName+'-CFGedgepaths.txt')
    originalVersionMapping = os.path.join(os.path.abspath(originalVersion),sourceClassName+'-CFGmapping.json')
    newVersionMapping = os.path.join(os.path.abspath(newVersion),sourceClassName+'-CFGmapping.json')
    #open all files
    # oldFile = open(oldPathFile,'r')
    # newFile = open(newPathFile,'r')
    # mappingOfOld = open(mappingOfOld,'r')
    # mappingOfNew = open(mappingOfNew,'r')

    oldFile = open(originalVersionEdges,'r')
    newFile = open(newVersionEdges,'r')
    mappingOfOld = open(originalVersionMapping,'r')
    mappingOfNew = open(newVersionMapping,'r')

    oldMappingData = json.load(mappingOfOld)
    newMappingData = json.load(mappingOfNew)

    #convert from dict in list to dict
    oldMappingDict = convertJsonToDict(oldMappingData)
    newMappingDict = convertJsonToDict(newMappingData)



    #convert paths as string to list
    allOldPaths = allPaths(oldFile)
    allNewPaths = allPaths(newFile)


    oldRoots = list(set([i[0] for i in allOldPaths]))
    newRoots = list(set([i[0] for i in allNewPaths]))
    #nodesInAFunc = [{root:set() for root in roots}][0]
    nodesInOldVersion = getNodesByFunc(allOldPaths)
    nodesInNewVersion = getNodesByFunc(allNewPaths)
    #print("NODES IN OLD",nodesInOldVersion)
    #print("NODES IN NEW",nodesInNewVersion)

    ClosestMatchStatements={}
    PerfectMatchStatements={}
    for root, oldNodes in nodesInOldVersion.items():
        newNodes = nodesInNewVersion[root]
        statements=[]
        for node_o in oldNodes:
            if node_o in oldMappingDict:
                oldStatement = oldMappingDict[node_o]['statement']
                for node_n in newNodes:
                    if node_n in newMappingDict:
                        newStatement = newMappingDict[node_n]['statement']
                        s = SequenceMatcher(None, oldStatement,newStatement).ratio();
                        if(s==1):                                                     #close statements to actually compare individual characters
                            PerfectMatchStatements[node_o]=node_n
                        elif(1>s>=0.6):
                            ClosestMatchStatements[node_o]=node_n


    #print("Perfect match pair of old:new",PerfectMatchStatements)
    #print("Closest match pair of old:new", ClosestMatchStatements)

    TrackChangeInOldVersion = defaultdict(set)
    TrackAdditionInNewVersion = defaultdict(set)
    TrackRemovalInOldVersion = defaultdict(set)



    for root, nodes in nodesInOldVersion.items():       #if perfectMatch doesn't exist for old code, statements are either removed or changed
        for node in nodes:
            if node not in PerfectMatchStatements:
                if node not in ClosestMatchStatements:
                    TrackRemovalInOldVersion[root].add(node)
                else:
                    TrackChangeInOldVersion[root].add(node)


                #TrackChangeInOldVersion[root] = node

    for root, nodes in nodesInNewVersion.items():      #if perfectMatch doesn't exist for new, they are new statements
        for node in nodes:
            if node not in [v for k,v in PerfectMatchStatements.items()] and node not in [v for k,v in ClosestMatchStatements.items()]:
                TrackAdditionInNewVersion[root] = node

    if TrackChangeInOldVersion:
        print("THESE LINES WERE CHANGED IN OLD VERSION {rootNode: changedNodes}",TrackChangeInOldVersion)
    elif TrackAdditionInNewVersion:
        print("THESE LINES WERE ADDED IN NEW VERSION {rootNode: changedNodes}",TrackAdditionInNewVersion)
    else:
        print("NO CHANGE IN SOURCE CODE")





    oldFile.close()
    newFile.close()

    mappingOfSmartTestInfo = open(os.path.dirname(originalVersion)+os.path.sep+"SmartTestData.json",'r')

    smartTestData = json.load(mappingOfSmartTestInfo)
    smartDataDict = convertJsonToDict(smartTestData)

    for rootNode,changedNodes in TrackChangeInOldVersion.items():
        for changedNode in changedNodes:
            changedStatementNumber = oldMappingDict[changedNode]['line']
            affectedRequirements = [key  for (key, value) in smartDataDict['requirements'].items() if changedStatementNumber in value]
            print("THESE REQUIREMENTS WERE AFFECTED",affectedRequirements)
            for affectedRequirement in affectedRequirements:
                satisfyFlag=False
                for testName,satisfiedReq in smartDataDict['testCoverage'].items():
                    if affectedRequirement in satisfiedReq:
                        satisfyFlag=True
                        affectedTest=testName
                        print("Rerun test:------>",affectedTest,"to check requirement ",affectedRequirement)
                        projectPath = os.path.dirname(os.getcwd())
                        os.chdir(projectPath)
                        #mvn -Dtest=TestClassName#testName test
                        print(f'Running test:-------> {affectedTest}')
                        subprocess.call(["mvn", "-Dtest=MethodTraceIT#"+affectedTest, "test"], shell=True)
                if not satisfyFlag:
                    print("Write new test for ",affectedRequirement,". No tests satisfy it!")





if __name__=='__main__':
    main()
