import pygraphviz
from networkx.drawing import nx_agraph
import networkx as nx
import sys
import json
import os
import collections

# INPUT FILE: source-CFG.dot
# OUTPUT FILE: source-edgeCoverageRequirements.txt, source-CFGmapping.json, source-CFGnodeGrpByFunction.txt


def createMappingFromDot(baseDir, dotinput):
    labels=[]
    '''
    creates mapping of CFG node to the line number and code statement
    '''

    with open(baseDir+os.path.sep+dotinput,'r') as dotfile:
        for line in dotfile:
            line=line.strip()
            line=line.strip('\"];')
            if '// graph-edges' in line:
                break
            if line and line[0]=='v':
                try:
                    info=[l.strip() for l in line.split(':') if l.strip()]
                    verlab=[l.strip() for l in info[0].split(' ') if l.strip()]
                    vertex=verlab[0]                                        #node
                    label=verlab[1].split('=')[1].strip().replace('"','') #lineNumber
                    classinfo=info[1]                                       #statement
                    labels.append([vertex,label,classinfo])
                except Exception as e:
                    info=[l.strip() for l in line.split('=') if l.strip()]
                    vertex=[l.strip() for l in info[0].split(' ') if l.strip()][0] #node
                    label=verlab[1].split('=')[1].strip().replace('"','') #lineNumber
                    classinfo=info[1]
                    labels.append([vertex,0,classinfo])   #statement
        with open(baseDir+os.path.sep+dotinput.split('.')[0]+'mapping.json', 'w') as mappingFile:
            todump=[]
            for label in labels:
                label={label[0]:{'line':label[1],'statement':label[2]}}
                todump.append(label)
            json.dump(todump,mappingFile,indent=2)
            print(mappingFile.name," CREATED")
            # mappingFile.write(label[0]+','+label[1]+','+label[2]+'\n')
    return labels

def createNodeGroupsByMethod(allPaths, baseDir, sourceFileName):
    '''
    dumps nodes grouped by the method that they belong to. Includes root node as well as child node in a method.
    Need in comparison later.
    '''
    with open(baseDir+os.path.sep+sourceFileName.split('.')[0]+'nodeGrpByFunction.json','w') as f:
        toDump=[]
        for root,childNodes in allPaths.items():
            childNodes.add(root)
            childWithRoot=list(childNodes)
            tempMap = {int(item[1:]):item for item in childWithRoot}
            od = collections.OrderedDict(sorted(tempMap.items()))
            sortedChildNodes = [v for k,v in od.items()]
            # childWithRoot=sorted(list(childNodes))
            label = {root:sortedChildNodes}
            toDump.append(label)
        # allNodesByFunc = str(allPaths).split("},")
        # for grp in allNodesByFunc:
        json.dump(toDump,f)
            # f.write(str(root)+':'+str(childNodes))
            # f.write('\n')
        print(f.name," CREATED")

# def createEdgePath(roots, baseDir, sourceFileName): #STORES ROOTS FOR LATER, NEED TO MAKE CHANGE IN COMPARATORS
#     with open(baseDir+os.path.sep+sourceFileName.split('.')[0]+'edgepaths.txt','w') as f:
#         for root in roots:
#             # print(root)
#             f.write(str(root)+',')
#             f.write('\n')
#         print(f.name," CREATED")


def createSimplePaths(roots,leaves,digraphobject):
    '''
    Find all loopless path between roots and leaves
    '''
    allPaths =[]
    for root in roots:
        for leaf in leaves:
            newRoot=""
            for allPath in nx.all_simple_paths(digraphobject,source=root, target=leaf):
                allPaths.append(allPath)
    return allPaths

def findPotentialLoops(edges, digraphobject,loops):
    '''
    If there is an edge from vLargerNumber to vSmallerNumber, there could be a loop and save that
    '''
    for start, end in edges:
        if int(start[1:])>int(end[1:]) and nx.has_path(digraphobject, end,start):
          loops.append((start,end))
    return loops

def createSubPathForLoops(loops, digraphobject, subPathForLoops):
    '''
    Find all simple path between loop start node and loop end node
    '''
    for loop in loops:
        for path in nx.all_simple_paths(digraphobject,source=loop[1], target=loop[0]):
            subPathForLoops.append({loop:path})
    return subPathForLoops

def addPathWithLoops(subPathForLoops, allPaths):
    '''
    Find all loopless path between roots and leaves
    '''
    for loopsToWorkOn in subPathForLoops:
        print(loopsToWorkOn)
        for loopToAdd,pathToAdd in loopsToWorkOn.items():
            toModifyList=[p for p in allPaths if loopToAdd[0] in p]
            for modifyPath in toModifyList:
                nodeindex=modifyPath.index(loopToAdd[0])
                newPath=modifyPath[0:nodeindex+1]+pathToAdd+modifyPath[nodeindex+1:]
                allPaths.append(newPath)
    return allPaths

def createEdgeRequirements(edges, baseDir, sourceFileName):
    with open(baseDir+os.path.sep+sourceFileName.split('.')[0]+'edgeCoverageRequirements.txt','w') as f:
        for edge in edges:
            newline=""
            for p in edge:
                if(newline!=""):
                    newline=newline+","+str(p)
                else:
                    newline=str(p)
            f.write(newline)
            f.write('\n')
        print(f.name," CREATED")

def main():
    if(len(sys.argv)>1):
        version=sys.argv[-1]
        sourceClass = sys.argv[-2]
    else:
        print('Usage: python3 graphparser <sourceClass> ../output/<version>\nSource without .java')
        return
    dotFileName = sourceClass+'-CFG.dot'
    print("CFG GRAPH PARSING STARTED OF...",sourceClass+".java")
    baseDir = os.path.abspath(version)

    abspathofDotFile=baseDir+os.path.sep+dotFileName
    try:
        labels=createMappingFromDot(baseDir,dotFileName)
    except OSError as e:
        print("No dot file present!")
        return
    dotobject=nx_agraph.read_dot(abspathofDotFile)
    digraphobject=nx.DiGraph(dotobject)

    roots = [k for k,v in digraphobject.in_degree() if v==0]
    leaves = [k for k,v in digraphobject.out_degree() if v==0]
    edges = digraphobject.edges()
    #print(edges)
    createEdgeRequirements(edges, baseDir, dotFileName)
    allNodesInAFunc ={}
    for root in roots:
        des = nx.algorithms.dag.descendants(digraphobject,root)
        allNodesInAFunc[root]=des
    createNodeGroupsByMethod(allNodesInAFunc,baseDir,dotFileName)

    # print(allNodesInAFunc)

    # allPaths = createSimplePaths(roots, leaves, digraphobject)
    #
    # loops=[]
    # loops = findPotentialLoops(edges,digraphobject,loops)
    #
    # subPathForLoops=[]
    # subPathForLoops = createSubPathForLoops(loops,digraphobject,subPathForLoops)
    # print(subPathForLoops,"---------SUBPATH FOR LOOPS")
    # # print(allPaths,"-----------ALLPATH")
    # allPaths = addPathWithLoops(subPathForLoops, allPaths)
    # print(allPaths)
    # createEdgePath(roots,baseDir, dotFileName)


if __name__=='__main__':
    main()
