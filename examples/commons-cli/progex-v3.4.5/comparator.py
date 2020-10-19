import sys
import json
from collections import defaultdict
from difflib import SequenceMatcher

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
        oldPathFile=sys.argv[-1]
        mappingOfOld=sys.argv[-2]
        newPathFile=sys.argv[-3]
        mappingOfNew=sys.argv[-4]

    else:
        print('Usage: python3 comparator.py mappingOfNew newPathFile mappingOfOld oldPathFile. Example: python3 comparator.py 1dotmapping0.json edgepaths_copy.txt 1dotmapping.json edgepaths.txt')
        return

    #open all files
    oldFile = open(oldPathFile,'r')
    newFile = open(newPathFile,'r')
    mappingOfOld = open(mappingOfOld,'r')
    mappingOfNew = open(mappingOfNew,'r')


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
    print("NODES IN OLD",nodesInOldVersion)
    print("NODES IN NEW",nodesInNewVersion)

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


    print("Perfect matches",PerfectMatchStatements)
    print("Closest matches", ClosestMatchStatements)

    TrackChangeInOldVersion = defaultdict(set)
    TrackAdditionInNewVersion = defaultdict(set)


    for root, nodes in nodesInOldVersion.items():       #if perfectMatch doesn't exist for old code, statements are either removed or changed
        for node in nodes:
            if node not in PerfectMatchStatements:
                TrackChangeInOldVersion[root] = node

    for root, nodes in nodesInNewVersion.items():      #if perfectMatch doesn't exist for new, they are new statements
        for node in nodes:
            if node not in [v for k,v in PerfectMatchStatements.items()]:
                TrackAdditionInNewVersion[root] = node

    if TrackChangeInOldVersion or TrackAdditionInNewVersion:
        print("THESE LINES WERE CHANGED IN OLD VERSION",TrackChangeInOldVersion)
        print("THESE LINES WERE ADDED IN NEW VERSION",TrackAdditionInNewVersion)
    else:
        print("NO CHANGE IN SOURCE CODE")





    oldFile.close()
    newFile.close()





if __name__=='__main__':
    main()
