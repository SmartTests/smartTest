import sys, os
import json
from collections import defaultdict
from difflib import SequenceMatcher
import subprocess
import itertools

# Last modified July 27, 2020 by Kesina Baral
# To do: Comment test in test file if all requirements are gone
# INPUT FILE: source-CFGnodeGrpByFunction.txt,source-CFGmapping.json, source-SmartTestData.json
# OUTPUT FILE: NONE, result shown on command line

#use printlog method to print all class attribute STATUS

#Note: PerfectMatchStatements and ClosestMatchStatements are used to store data but never used for comparison due to additional loop cost it brings




class Comparator:
    def __init__(self, originalVersion,newVersion,sourceClassName):
        self.originalVersion = originalVersion
        self.newVersion = newVersion
        self.sourceClassName = sourceClassName
        self.ClosestMatchStatements = {}
        self.closestMatchedOldNode = set()
        self.closestMatchedNewNode = set()

        self.PerfectMatchStatements = {}
        self.perfectMatchedOldNode = set()
        self.perfectMatchedNewNode = set()

        self.newTestRequirements = defaultdict(set)
        self.affectedTest = defaultdict(set)
        self.deletedTest = defaultdict() #was defaultdict(set) but not needed
        self.testWithDeletedRequirement = defaultdict(set)
        self.unsatisfiedRequirement = set()
        self.deletedRequirement = set()
        self.TrackChangeInOldVersion = defaultdict(set)
        self.TrackAdditionInNewVersion = defaultdict(set)
        self.TrackRemovalInOldVersion = defaultdict(set)
        self.deletedNodes=[]
        self.affectedReqSet=set()
        self.minimal=True
        self.minimalAffectedTest = []
        self.lineReplaced=False

        self.resultMap= defaultdict(dict)
        self.projectPath=''
        self.failedTest=[]




    def convertJsonToDict(self,jsonMapping):
        mappingDict = dict()
        for data in jsonMapping:
            for k,v in data.items():
                mappingDict[k]=v
        return mappingDict

    def allPaths(self,nodeGrpByFunctionFile):  #convert nodeGrpByFunction as text to list
        allPaths=[]
        for path in nodeGrpByFunctionFile:  #from nodeGrpByFunction file
            path = path.strip().strip(',').split(",")
            allPaths.append(path)
        return allPaths

    # def getNodesByFunc(self,allPaths):
    #     nodesInFuncs = defaultdict(set)
    #     for path in allPaths:
    #         for i in path:
    #             nodesInFuncs[path[0]].add(i)
    #     return nodesInFuncs
    # def getNodesByFunc(self,allText):
    #     nodesInFuncs = {}
    #     roots = [root for root,child in nodeGroup for nodeGroup in allText]
    #
    #     for entry in allPaths:
    #         e = entry.split(":")
    #         nodesInFuncs[e[0]]=e[1].strip()
    #     return nodesInFuncs

    def getRelevantData(self,fileDir,fileName,extension):
        if "Smart" in extension:
            file = os.path.join(os.path.dirname(fileDir),fileName+extension)
        else:
            file = os.path.join(os.path.abspath(fileDir),fileName+extension)
        fileContentStream = open(file,'r')

        if('json' in extension):
            fileContent = json.load(fileContentStream)
        else:
            fileContent= fileContentStream.readlines()

        fileContentStream.close()
        return fileContent

    def checkIfPerfectMatchOfBaseExists(self,allBaseText, oldMappingDict):
        for nodesInBaseVersion in allBaseText:
            for root, nodes in nodesInBaseVersion.items():       #if perfectMatch doesn't exist for old code, statements are either removed or changed
                for node in nodes:
                    if oldMappingDict[node]['statement'] !="\"endif":
                        if node not in self.perfectMatchedOldNode:
                            if node not in self.closestMatchedOldNode:
                                self.TrackRemovalInOldVersion[root].add(node)
                            else:
                                self.TrackChangeInOldVersion[root].add(node)
                        # if node not in self.PerfectMatchStatements:
                        #     if node not in self.ClosestMatchStatements:
                        #         self.TrackRemovalInOldVersion[root].add(node)
                        #     else:
                        #         self.TrackChangeInOldVersion[root].add(node)
        # print(self.TrackChangeInOldVersion,"-------------HERE------------")

    def checkIfNewStatementsAddedInNewVersion(self,allNewText,newMappingDict):
        for nodesInNewVersion in allNewText:
            for root, nodes in nodesInNewVersion.items():      #if perfectMatch doesn't exist for new, they are new statements
                for node in nodes:
                    if newMappingDict[node]['statement'] !="\"endif":
                        if node not in self.perfectMatchedNewNode and node not in self.closestMatchedNewNode:
                            self.TrackAdditionInNewVersion[root].add(node)
                        # if node not in [v for k,v in self.PerfectMatchStatements.items()] and node not in [v for k,v in self.ClosestMatchStatements.items()]:
                        #     self.TrackAdditionInNewVersion[root].add(node)


    def findMethodStart(self,oldMappingDict, newMappingDict, oldNode,modifiedCFGRoots):
        oldRootStatement = oldMappingDict[oldNode]['statement']
        for newRoot in modifiedCFGRoots:
            newRootStatement = newMappingDict[newRoot]['statement']
            s = SequenceMatcher(None, oldRootStatement,newRootStatement).ratio();
            if(s==1):                                                     #close statements to actually compare individual characters
                return newRoot

    def compareStatementsWithinAMethod(self,allBaseText,allNewText,oldMappingDict,newMappingDict,modifiedCFGRoots):
        '''compares statements using SequenceMatcher and categorizes as perfect match or close match. Starts
        by matching the root of the method. Finds a matching root and compares nodes under two matching roots.
        This is to avoid matching between two different methods.

        '''
        for nodesInBaseVersion in allBaseText:
            for root, oldNodes in nodesInBaseVersion.items():
                newNodes  = [v for nodesInModifiedVersion in allNewText for k,v in nodesInModifiedVersion.items() if k == root]
                # newNodes = nodesInModifiedVersion[root]
                if newNodes:
                    newNodes = newNodes[0]
                    oldRootStatement = oldMappingDict[root]['statement']
                    newRootStatement = newMappingDict[root]['statement']
                    s = SequenceMatcher(None, oldRootStatement,newRootStatement).ratio();
                    if(s==1):                                                     #close statements to actually compare individual characters
                        self.PerfectMatchStatements[root] = root
                        self.perfectMatchedNewNode.add(root)
                        self.perfectMatchedOldNode.add(root)
                    else:
                        newRoot=self.findMethodStart(oldMappingDict,newMappingDict,root,modifiedCFGRoots) # if the root node was shifted, the start of method won't be found so search by statement
                        if newRoot:
                            self.PerfectMatchStatements[root]=newRoot
                            self.perfectMatchedNewNode.add(newRoot)
                            self.perfectMatchedOldNode.add(root)
                            newNodes  = [v for nodesInModifiedVersion in allNewText for k,v in nodesInModifiedVersion.items() if k == newRoot][0]
                            # newNodes = nodesInModifiedVersion[newRoot]
                else:
                    newRoot=self.findMethodStart(oldMappingDict,newMappingDict,root,modifiedCFGRoots)
                    if newRoot:
                        self.PerfectMatchStatements[root]=newRoot
                        self.perfectMatchedNewNode.add(newRoot)
                        self.perfectMatchedOldNode.add(root)

                        newNodes  = [v for nodesInModifiedVersion in allNewText for k,v in nodesInModifiedVersion.items() if k == newRoot ][0]

                        # newNodes = nodesInModifiedVersion[newRoot]


                index=0
                for node_o in oldNodes:
                    if node_o in oldMappingDict:
                        searchFromNode=index
                        oldStatement = oldMappingDict[node_o]['statement']
                        for i in range(searchFromNode,len(newNodes)):
                            node_n= newNodes[i]
                        # for node_n in newNodes:
                            if node_n in newMappingDict:
                                newStatement = newMappingDict[node_n]['statement']
                                s = SequenceMatcher(None, oldStatement,newStatement).ratio();
                                if(s==1):  #close statements to actually compare individual characters
                                    self.perfectMatchedNewNode.add(node_n)
                                    self.perfectMatchedOldNode.add(node_o)
                                    self.PerfectMatchStatements[node_o]=node_n
                                    index=i+1
                                elif(1>s>=0.6):
                                    self.ClosestMatchStatements[node_o]=node_n
                                    self.closestMatchedOldNode.add(node_o)
                                    self.closestMatchedNewNode.add(node_n)
                                    index=i+1
                                break

        # print(self.perfectMatchedNewNode,"perfect new-----------")
        # print(self.perfectMatchedOldNode,"perfect old-----------")
        # print(self.PerfectMatchStatements,"all match----------")


    def checkRequirementForEdit(self,oldMappingDict,smartDataDict):
        for rootNode,changedNodes in self.TrackChangeInOldVersion.items():
            for changedNode in changedNodes:
                changedStatementNumber = oldMappingDict[changedNode]['line']
                affectedRequirements=[]
                for key, value in smartDataDict['requirements'].items():
                    tempListForChecking = value.split(",")
                    if changedStatementNumber == tempListForChecking[0] or changedStatementNumber == tempListForChecking[1]:
                        affectedRequirements.append(key)
                # affectedRequirements = [key  for (key, value) in smartDataDict['requirements'].items() if changedStatementNumber in value]
                for affectedRequirement in affectedRequirements:
                    requirementIsSatisifed=False
                    self.affectedReqSet.add(affectedRequirement)
                    for testName,satisfiedReq in smartDataDict['testCoverage'].items():
                        if affectedRequirement in satisfiedReq:
                            requirementIsSatisifed=True
                            self.affectedTest[testName].add(affectedRequirement)
                    if not requirementIsSatisifed:
                        self.unsatisfiedRequirement.add(affectedRequirement)

    def checkRequirementForAddition(self,newMappingDict,smartDataDict, nodeGrpByFunctionInBase,oldMappingDict,oldEdgesCollection,newEdgesCollection):
        # print("addition--------",self.TrackAdditionInNewVersion)
        # print(newEdgesCollection)
        newEdgesCollectionList=[]
        affectedRequirementList=[]
        counter=1
        for line in newEdgesCollection:
            edgeMaps={}
            nodes = line.strip().split(",")
            edgeMaps[nodes[0]] = nodes[1]
            newEdgesCollectionList.append(edgeMaps)
        for rootNode,addedNodes in self.TrackAdditionInNewVersion.items():
            for addedNode in addedNodes:
                addedStatementNumber = newMappingDict[addedNode]['line']
                nodesAfterAddedNode = [v for items in newEdgesCollectionList for k,v in items.items() if k==addedNode]
                nodesBeforeAddedNode = [k for items in newEdgesCollectionList for k,v in items.items() if v==addedNode]
                previousStatementNumbers=[]
                nextStatementNumbers=[]

                for node in nodesBeforeAddedNode:
                    '''
                    There could be multiple previous nodes so find the list of previous lines.
                    Previous node might be 'endfor' or 'endif' statement i.e. line number =0. If so find a valid node with valid line number
                    '''
                    previousLine = newMappingDict[node]['line']
                    while previousLine==0:
                        counter=1
                        nodePreviousToAddedNode = "v"+str((int(node.split('v')[1])-counter))
                        validNode=newMappingDict.get(nodePreviousToAddedNode)
                        while not validNode:  #because addedNode-1 might not exist since dot file was cleaned
                            counter+=1
                            nodePreviousToAddedNode = "v"+str((int(node.split('v')[1])-counter))
                            validNode=newMappingDict.get(nodePreviousToAddedNode)
                        node=nodePreviousToAddedNode
                        previousLine=newMappingDict[nodePreviousToAddedNode]['line']

                    previousStatementNumbers.append(previousLine)

                for node in nodesAfterAddedNode:
                    '''
                    There could be multiple after nodes so find the list of after lines.
                    After node might be 'endfor' or 'endif' statement i.e. line number =0. If so find a valid node with valid line number
                    '''
                    nextLine = newMappingDict[node]['line']
                    while nextLine==0:
                        counter=1
                        nodeAfterAddedNode = "v"+str((int(node.split('v')[1])+counter))
                        validNode=newMappingDict.get(nodeAfterAddedNode)
                        while not validNode:  #because addedNode-1 might not exist since dot file was cleaned
                            counter+=1
                            nodeAfterAddedNode = "v"+str(int(node.split('v')[1])+counter)
                            validNode=newMappingDict.get(nodeAfterAddedNode)
                        node=nodeAfterAddedNode
                        nextLine=newMappingDict[nodeAfterAddedNode]['line']

                    nextStatement = newMappingDict[node]['statement']
                    sibilingNodesOfAddedNode = [child for items in nodeGrpByFunctionInBase for root,child in items.items() if root==rootNode]
                    if sibilingNodesOfAddedNode:
                        sibilingNodesOfAddedNode = sibilingNodesOfAddedNode[0]
                    for node in sibilingNodesOfAddedNode:
                        # print(node)
                        searchStmt = oldMappingDict[node]['statement']
                        if searchStmt == nextStatement:
                            nextLine = oldMappingDict[node]['line']
                            break
                    nextStatementNumbers.append(nextLine)

                if(previousStatementNumbers and nextStatementNumbers): #if node2 inserted between two existing nodes: node1 and node 3 -> node1,node3 is affected, two new req created
                    seriallyGeneratedEdges = [(x,y) for x in previousStatementNumbers for y in nextStatementNumbers]
                    reverseGeneratedEdges = [(y,x) for x in previousStatementNumbers for y in nextStatementNumbers]
                    potentiallyAffectedRequirements = seriallyGeneratedEdges+reverseGeneratedEdges
                    for edge in potentiallyAffectedRequirements:
                        edgeToSearchFor = edge[0]+","+edge[1]
                        affectedRequirements= [key  for (key, value) in smartDataDict['requirements'].items() if value==edgeToSearchFor]
                        #.startswith(previousStatementNumber) and value.endswith(nextStatementNumber) ]
                        if affectedRequirements:  #no edge might be present between previous and next statement
                            affectedRequirementList.append(affectedRequirements[0])
                            self.newTestRequirements[affectedRequirements[0]].add(str(edge[0])+','+str(addedStatementNumber))
                            self.newTestRequirements[affectedRequirements[0]].add(str(addedStatementNumber)+','+str(edge[1]))
                else:
                    if(previousStatementNumbers):
                        for previousStatementNumber in previousStatementNumbers:
                            affectedRequirements= [key  for (key, value) in smartDataDict['requirements'].items() if value.startswith(previousStatementNumber) and value.endswith(str(addedStatementNumber)) ]
                            if affectedRequirements: # might not have edge from previous node
                                affectedRequirementList.append(affectedRequirements[0])
                                self.newTestRequirements[affectedRequirements[0]].add(str(previousStatementNumber)+','+str(addedStatementNumber))
                    if(nextStatementNumbers):
                        for nextStatementNumber in nextStatementNumbers:
                            affectedRequirements= [key  for (key, value) in smartDataDict['requirements'].items() if value.startswith(addedStatementNumber) and value.endswith(nextStatementNumber) ]
                            if affectedRequirements: # might not have edge to next node
                                affectedRequirementList.append(affectedRequirements[0])
                                self.newTestRequirements[affectedRequirements[0]].add(str(addedStatementNumber)+','+str(nextStatementNumber))
                for affectedRequirement in affectedRequirementList:
                    requirementIsSatisifed = False
                    self.affectedReqSet.add(affectedRequirement)
                    for testName,satisfiedReq in smartDataDict['testCoverage'].items():
                        if affectedRequirement in satisfiedReq:
                            requirementIsSatisifed = True
                            self.affectedTest[testName].add(affectedRequirement)
                    if not requirementIsSatisifed:
                        self.unsatisfiedRequirement.add(affectedRequirement)

    def returnLinesFromTracker(self, trackerName, mappingDict):
        if trackerName == "TrackChangeInOldVersion":
            tracker = self.TrackChangeInOldVersion
        elif trackerName == "TrackAdditionInNewVersion":
            tracker = self.TrackAdditionInNewVersion
        elif trackerName == "TrackRemovalInOldVersion":
            tracker = self.TrackRemovalInOldVersion
        tempSet=set()
        for key,values in tracker.items():
            for value in values:
                line = mappingDict[value]['line']
                tempSet.add(line)
        return tempSet

    def storeSourceCodeInfo(self,dataLabel,data,sourceName):
        tempMap = {}
        tempMap[dataLabel]=list(data)
        tempMap["sourceClass"]=sourceName
        self.resultMap["sourceCodeStatus"]=tempMap


    def checkIfChangeInSourceCode(self,oldMappingDict,newMappingDict,sourceClassName):
        print("==============================")
        print("SOURCE CODE STATUS")
        print("==============================")
        someChange = False

        if self.TrackAdditionInNewVersion and self.TrackRemovalInOldVersion:
            addedLine = self.returnLinesFromTracker("TrackAdditionInNewVersion",newMappingDict)
            deletedLine = self.returnLinesFromTracker("TrackRemovalInOldVersion",oldMappingDict)
            if addedLine == deletedLine:
                print("LINE",addedLine, "OF OLD VERSION OF",sourceClassName,"REPLACED")
                self.storeSourceCodeInfo("line",addedLine,sourceClassName)
                self.lineReplaced= True
        if not self.lineReplaced:
            if self.TrackChangeInOldVersion:
                tempSet = self.returnLinesFromTracker("TrackChangeInOldVersion",oldMappingDict)
                if len(tempSet)>1:
                    print("LINES",tempSet, "OF OLD VERSION OF",sourceClassName,"CHANGED")
                else:
                    print("LINE",tempSet, "OF OLD VERSION OF",sourceClassName,"CHANGED")
                self.storeSourceCodeInfo("line",tempSet,sourceClassName)
                someChange = True
            if self.TrackAdditionInNewVersion:
                tempSet = self.returnLinesFromTracker("TrackAdditionInNewVersion",newMappingDict)
                if len(tempSet)>1:
                    print("NEW STATEMENT ADDED IN LINES",tempSet, "IN NEW VERSION OF",sourceClassName)
                else:
                    print("NEW STATEMENT ADDED IN LINE",tempSet, "IN NEW VERSION OF",sourceClassName)
                self.storeSourceCodeInfo("line",tempSet,sourceClassName)
                someChange = True
            if self.TrackRemovalInOldVersion:
                tempSet = self.returnLinesFromTracker("TrackRemovalInOldVersion",oldMappingDict)
                if len(tempSet)>1:
                    print("LINES",tempSet, "DELETED IN NEW VERSION OF",sourceClassName)
                else:
                    print("LINE",tempSet, "DELETED IN NEW VERSION OF",sourceClassName)
                self.storeSourceCodeInfo("line",tempSet,sourceClassName)
                someChange = True
            if not someChange:
                print("NO CHANGE IN SOURCE CODE", "of",sourceClassName)


    def reRunTest(self,sourceClassName, smartDataDict):
        projectPath = os.path.dirname(os.getcwd())
        os.chdir(projectPath)
        if self.minimal:
            testSet = set()
            testToReRun = set()
            testPair = defaultdict(set)
            for test,affectedRequirement in self.affectedTest.items():
                testSet.add(test) # 1.s,2.s,3.s,4.s  => 1,2
            testToReRun = testSet.copy()
            testSet = list(testSet)
            for i in range(len(testSet)):
                reqList1 = smartDataDict['testCoverage'][testSet[i]]
                j = i+1
                for j in range(i+1,len(testSet)):
                    reqList2 = smartDataDict['testCoverage'][testSet[j]]
                    if reqList1 == reqList2:
                        testPair[testSet[i]].add(testSet[j])
            for key,value in testPair.items():
                for v in value:
                    if(v in testSet):
                        testSet.remove(v)
        else:
            testToReRun = self.affectedTest.keys()

        self.minimalAffectedTest=testToReRun
        # for test in testToReRun:
        #     print("RUNNING TEST",test)
        #     testRunningCommand="mvn"+" -Dtest="+sourceClassName+"TestIT#"+test+" test -q"
        #     try:
        #         subprocess.run(testRunningCommand,shell=True, check=True)
        #     except subprocess.CalledProcessError:
        #         # print(test)
        #         self.failedTest.append(test)


    def storeTestCodeInfo(self,dataLabel,data):
        self.resultMap["testCodeStatus"][dataLabel]=list(data)

    def printComparisonResult(self):
        print("==============================")
        print("TEST CODE STATUS")
        print("==============================")
        if self.affectedReqSet:
            print("==============================")
            print("Affected Requirements")
            print("==============================")
            sortingTempList=[]
            self.storeTestCodeInfo("affectedReq",self.affectedReqSet)
            for req in self.affectedReqSet:
                sortingTempList.append(int(req[2:]))
            for value in sorted(sortingTempList):
                print('TR'+str(value))

        if self.deletedRequirement:
            print("==============================")
            print("Deleted Requirements")
            print("==============================")
            if self.deletedTest:
                self.storeTestCodeInfo("deletedTest",self.deletedTest)
                for test, requirement in self.deletedTest.items():
                    self.storeTestCodeInfo("deletedTest",self.deletedTest)
                    print("Remove test",test,"requirement",requirement,"no longer present")
            if self.deletedRequirement:
                for req in self.deletedRequirement:
                    if self.testWithDeletedRequirement:
                        self.storeTestCodeInfo("deletedRequirementYesTest",self.deletedRequirement)
                        tests= [test for test, requirement in self.testWithDeletedRequirement.items() if req in requirement]
                        print("Requirement",req,"no longer present. Test",tests,"was satisfying it.")
                    else:
                        self.storeTestCodeInfo("deletedRequirementNoTest",self.deletedRequirement)
                        for req in self.deletedRequirement:
                            print("Requirement",req,"no longer present. No tests were satisfying it.")
        if( not self.affectedReqSet and not self.deletedRequirement ):
            print("NO REQUIREMENTS WERE AFFECTED DUE TO THE CHANGE!")

        if self.affectedTest:
            print("==============================")
            print("Affected Tests")
            print("==============================")
            self.storeTestCodeInfo("affectedTest",self.affectedTest)
            for test, affectedRequirement in self.affectedTest.items():
                print("Rerun test:------>",test,"to check requirement ",affectedRequirement)
            print("==============================")
            if self.minimal:
                print("Minimal Tests Re-ran")
            else:
                print("Tests Re-ran")
            print("==============================")
            self.storeTestCodeInfo("testReran",self.minimalAffectedTest)
            for test in self.minimalAffectedTest:
                print("Reran test:------>",test)
        else:
            print("NO TESTS NEED TO BE RE-RUN!")

        if self.unsatisfiedRequirement:
            print("==============================")
            print("Unsatisfied Test Requirements")
            print("==============================")
            self.storeTestCodeInfo("unsatisfiedRequirement",self.unsatisfiedRequirement)
            for req in self.unsatisfiedRequirement:
                print("Write new test for ",req,". No tests satisfy it!")

        if self.newTestRequirements:
            print("==============================")
            print("New Requirements")
            print("==============================")
            self.storeTestCodeInfo("newTestRequirement",self.newTestRequirements)
            for reqName, newLines in self.newTestRequirements.items():
                for newLine in newLines:
                    if self.lineReplaced: # tO do
                        print("New requirement ",newLine,"created. Requirement",reqName,'might no longer exist!')
                    else:
                        print("New requirement ",newLine,"created. Requirement",reqName,'might no longer exist!')



    def storeResult(self,sourceClassName,newVersion):
        pathToOutputFolder = self.projectPath+os.path.sep+"finalResult" #+os.path.sep+"finalResult-"+sourceClassName
        # os.mkdir(pathToOutputFolder)
        outputJsonFile = sourceClassName+"-"+newVersion+".json"
        # toDump=[]
        if self.failedTest:
            self.resultMap["failedTest"]=self.failedTest
        # if(self.resultMap):

        print(json.dumps(self.resultMap))
        with open(pathToOutputFolder+os.path.sep+outputJsonFile, 'w') as mappingFile:
            json.dump(self.resultMap,mappingFile,indent=2)


    def printLog(self):
        print("-------------CLASS INFO----------------------")
        print(self.originalVersion,"----OriginalVersion-------")
        print(self.newVersion,"----newVersion-------")
        print(self.sourceClassName,"----Source class name-------")
        print("-------------MATCH STATUS----------------------")
        print(self.ClosestMatchStatements,"-----ClosestMatchStatements------")
        print(self.PerfectMatchStatements,"-----PerfectMatchStatements------")
        print(self.deletedNodes,"-----deletedLines------")
        print(self.TrackChangeInOldVersion,"-----TrackChangeInOldVersion------")
        print(self.TrackAdditionInNewVersion,"------TrackAdditionInNewVersion-----")
        print(self.TrackRemovalInOldVersion,"-----TrackRemovalInOldVersion------")
        print("-------------TEST STATUS----------------------")
        print(self.minimal,"----Minimal Test run?-------")
        print(self.affectedTest,"-----affectedTest------")
        print(self.deletedTest,"-----deletedTest------")
        print("-------------REQUIREMENT STATUS----------------------")
        print(self.affectedReqSet,"------Affected requirements-----")
        print(self.newTestRequirements,"-----newTestRequirements------")
        print(self.unsatisfiedRequirement,"-----unsatisfiedRequirement------")
        print(self.deletedRequirement,"-----deletedRequirement------")


    def checkRequirementForDeletion(self, oldMappingDict, smartDataDict):
        for rootNode,removedNodes in self.TrackRemovalInOldVersion.items():
            for removedNode in removedNodes:
                removedLine = oldMappingDict[removedNode]['line']
                self.deletedNodes.append(removedLine)


        for rootNode,removedNodes in self.TrackRemovalInOldVersion.items():
            for removedNode in removedNodes:
                removedStatementNumber = str(oldMappingDict[removedNode]['line'])
                affectedRequirements=[]
                for key, value in smartDataDict['requirements'].items():
                    tempListForChecking = value.split(",")
                    if removedStatementNumber in tempListForChecking:
                        affectedRequirements.append(key)
                # affectedRequirements = [key  for (key, value) in smartDataDict['requirements'].items() if removedStatementNumber in value ]
                for affectedRequirement in affectedRequirements:
                    satisfyFlag=False
                    self.affectedReqSet.add(affectedRequirement)
                    affectedLineNumbers = [value for (key,value) in smartDataDict['requirements'].items() if affectedRequirement==key ][0].split(",")
                    counter=0
                    for line in affectedLineNumbers:
                        if line in self.deletedNodes:
                            counter=counter+1
                    if counter == 2:
                        self.deletedRequirement.add(affectedRequirement)
                        self.affectedReqSet.remove(affectedRequirement)
                    for testName,satisfiedReq in smartDataDict['testCoverage'].items():
                        if affectedRequirement in satisfiedReq and affectedRequirement in self.deletedRequirement:
                            satisfyFlag=True
                            self.affectedTest[testName].add(affectedRequirement)
                            self.testWithDeletedRequirement[testName].add(affectedRequirement)
                        elif affectedRequirement in satisfiedReq and affectedRequirement not in self.deletedRequirement:
                            satisfyFlag=True
                            self.affectedTest[testName].add(affectedRequirement)
                    if not satisfyFlag:
                        self.unsatisfiedRequirement.add(affectedRequirement)

        if(self.affectedTest):
            for testName, deletedRequirement in self.affectedTest.items():
                satisfiedRequirement = smartDataDict['testCoverage'].get(testName)
                if sorted(satisfiedRequirement) == sorted(deletedRequirement):
                    # print(type(testName),"--test name---")
                    # print(type(deletedRequirement),"--------DR-------")
                    self.deletedTest[testName]=deletedRequirement





    def getRoots(self, allText):
        roots = []
        roots = [root for nodeGroup in allText for root,child in nodeGroup.items()]
        return roots

def main():
    if(len(sys.argv)>1):
        originalVersion = sys.argv[-2]
        newVersion = sys.argv[-1]
        sourceClassName = sys.argv[-3]
        comparator=Comparator(originalVersion,newVersion,sourceClassName)
    else:
        print('Example: python3 comparator.py SourceClass ../output/27-04-2020_17_01_08 ../output/27-04-2020_17_01_08')
        print('Usage: python3 comparator.py <SourceClassName> ../output/<originalVersionDir> ../output/<newVersionDir>')
        return
    try:
        nodeGrpByFunctionInBase = comparator.getRelevantData(originalVersion,sourceClassName,'-CFGnodeGrpByFunction.json')
    except OSError as e:
        print("File not found for class "+sourceClassName)
        return

    nodeGrpByFunctionInModified = comparator.getRelevantData(newVersion,sourceClassName,'-CFGnodeGrpByFunction.json')
    baseMapData = comparator.getRelevantData(originalVersion,sourceClassName,'-CFGmapping.json')
    modifiedMapData = comparator.getRelevantData(newVersion,sourceClassName,'-CFGmapping.json')
    smartTestDataJson = comparator.getRelevantData(originalVersion,sourceClassName,'-SmartTestData.json')
    smartTestData = comparator.convertJsonToDict(smartTestDataJson) #smartDataDict

    oldEdgesCollection=comparator.getRelevantData(originalVersion,sourceClassName,'-CFGedgeCoverageRequirements.txt')
    newEdgesCollection=comparator.getRelevantData(newVersion,sourceClassName,'-CFGedgeCoverageRequirements.txt')


    #convert from dict in list to dict
    oldMappingDict = comparator.convertJsonToDict(baseMapData)
    newMappingDict = comparator.convertJsonToDict(modifiedMapData)

    baseCFGRoots = comparator.getRoots(nodeGrpByFunctionInBase)
    modifiedCFGRoots = comparator.getRoots(nodeGrpByFunctionInModified)


    #find matching method between two versions and compare within it for any change
    comparator.compareStatementsWithinAMethod(nodeGrpByFunctionInBase,nodeGrpByFunctionInModified,oldMappingDict,newMappingDict,modifiedCFGRoots)

    #check if any edits or removal happened on base version
    comparator.checkIfPerfectMatchOfBaseExists(nodeGrpByFunctionInBase, oldMappingDict)

    #check if any new statements were added in new version
    comparator.checkIfNewStatementsAddedInNewVersion(nodeGrpByFunctionInModified, newMappingDict)

    #find requirements and tests affected by any code modification
    comparator.checkRequirementForEdit(oldMappingDict, smartTestData)
    #find requirements and tests affected by any code addition
    comparator.checkRequirementForAddition(newMappingDict, smartTestData, nodeGrpByFunctionInBase,oldMappingDict,oldEdgesCollection,newEdgesCollection)
    #find requirements and tests affected by any code deletion
    comparator.checkRequirementForDeletion(oldMappingDict, smartTestData)

    comparator.projectPath = os.path.dirname(os.getcwd())

    #re-run affected tests
    if comparator.affectedTest:
        comparator.reRunTest(sourceClassName,smartTestData)

    #print code status
    comparator.checkIfChangeInSourceCode(oldMappingDict,newMappingDict,sourceClassName)

    #print final result of comparison
    comparator.printComparisonResult()

    comparator.storeResult(sourceClassName,newVersion.split("/")[2])










if __name__=='__main__':
    main()
