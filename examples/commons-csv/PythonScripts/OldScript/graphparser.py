import pygraphviz
from networkx.drawing import nx_agraph
import networkx as nx
import sys
import json
import os

def createMappingFromDot(baseDir, dotinput):
    labels=[]

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

def createEdgePath(allPaths, baseDir, sourceFileName):
    with open(baseDir+os.path.sep+sourceFileName.split('.')[0]+'edgepaths.txt','w') as f:
        for path in allPaths:
            for p in path:
                f.write(str(p)+',')
            f.write('\n')
        print(f.name," CREATED")


def createSimplePaths(roots,leaves,digraphobject,allPaths):
    for root in roots:
        for leaf in leaves:
            newRoot=""
            for allPath in nx.all_simple_paths(digraphobject,source=root, target=leaf):
                allPaths.append(allPath)
    return allPaths

def findPotentialLoops(edges, digraphobject,loops):
    for start, end in edges:
        if int(start[1:])>int(end[1:]) and nx.has_path(digraphobject, end,start):
          loops.append((start,end))
    return loops

def createSubPathForLoops(loops, digraphobject, subPathForLoops):
    for loop in loops:
        for path in nx.all_simple_paths(digraphobject,source=loop[1], target=loop[0]):
            subPathForLoops.append({loop:path})
    return subPathForLoops

def addPathWithLoops(subPathForLoops, allPaths):
    for loopsToWorkOn in subPathForLoops:
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
    labels=createMappingFromDot(baseDir,dotFileName)
    dotobject=nx_agraph.read_dot(abspathofDotFile)
    digraphobject=nx.DiGraph(dotobject)

    roots = [k for k,v in digraphobject.in_degree() if v==0]
    leaves = [k for k,v in digraphobject.out_degree() if v==0]
    edges = digraphobject.edges()
    #print(edges)
    createEdgeRequirements(edges, baseDir, dotFileName)
    allPaths = []
    trackEdgeUse=dict()

    allPaths = createSimplePaths(roots, leaves, digraphobject, allPaths)

    loops=[]
    loops = findPotentialLoops(edges,digraphobject,loops)

    subPathForLoops=[]
    subPathForLoops = createSubPathForLoops(loops,digraphobject,subPathForLoops)

    allPaths = addPathWithLoops(subPathForLoops, allPaths)

    #print(allPaths)
    createEdgePath(allPaths,baseDir, dotFileName)


if __name__=='__main__':
    main()
