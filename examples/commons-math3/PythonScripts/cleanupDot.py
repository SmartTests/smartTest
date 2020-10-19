import os,sys
from collections import defaultdict

'''
CALLED IN runProgex.sh. No need to run separately.

Cleans up dot file. That is, CFG nodes of 'for loop' is divided into 3 nodes. Causes confusion during analysis so turned into 1 node.
Changes the edges accordingly. Rewrites the dot file after these changes. Commented code includes work to remove endIf and endFor nodes.
Okay to keep for now.
'''
version= sys.argv[-1]
fileName = sys.argv[-2]
fileDir =  os.path.abspath(version)

# fileName = "DerivativeStructure"
extension ="-CFG.dot"



def main():
    spreadStatements = defaultdict(set)
    relevantContent = []
    verticesFound=False
    edgesFound=False
    file = os.path.join(fileDir,fileName+extension)
    try:
        fileContentStream = open(file,'r')
        fileContent= fileContentStream.readlines()
        fileContentStream.close()
    except OSError as e:
        print("DOT FILE NOT THERE!")
        sys.exit()


    '''
    separate content in dot file
    '''
    for line in fileContent:
        if("  // graph-vertices" in line):
            verticesFound = True
            continue
        if verticesFound and "  // graph-edges" not in line:
            relevantContent.append(line)
        else:
            verticesFound = False

        '''
        find the for lines that are divided into multiple nodes
        '''
    for i in range(len(relevantContent)):
        firstLine = relevantContent[i].strip()
        nodeNumber1 = firstLine.split("=\"")[0].replace("[label","")
        if ":" in firstLine:
            lineNumber1 = firstLine.split("=\"")[1].split(":")[0]
            statement1 = firstLine.split(":")[1].replace("\"];","")
            statement1 = nodeNumber1+";;"+statement1
            for j in range(i+1,len(relevantContent)):
                secondLine = relevantContent[j].strip()
                nodeNumber2 = secondLine.split("=\"")[0].replace("[label","")
                if ":" in secondLine:
                    lineNumber2 = secondLine.split("=\"")[1].split(":")[0]
                    statement2 = secondLine.split(":")[1].replace("\"];","")
                    statement2 = nodeNumber2+";;"+statement2
                    if lineNumber1 == lineNumber2:
                        spreadStatements[lineNumber1].add(statement1)
                        spreadStatements[lineNumber1].add(statement2)
                else:
                    continue
        else:
            continue

    # ifReplacements={}
    # for i in range(len(relevantContent)):
    #     firstLine = relevantContent[i].strip()
    #     if "endif" in firstLine:
    #         unnecessaryNode = firstLine.split("[")[0]
    #         replacementNode = "v"+str(int(unnecessaryNode.replace("v",""))+1)
    #         ifReplacements[unnecessaryNode]=replacementNode

    # print(ifReplacements)

    '''
    find line numbers where for should be
    '''
    lineNumbersWithFor=[]
    for key, values in spreadStatements.items():
        for value in values:
            if "for" in value:
                lineNumbersWithFor.append(key)

                            # print(lineNumbersWithFor)
                            # for k,v in spreadStatements.items():
                            #     print(k,v)
    '''
    compress the spread for statement into one node and create the replacement statement
    = searched in case the loop variable to declared before the loop
    '''
    statementsToBeCompiled ={}
    for line in lineNumbersWithFor:
        finalStatementOrder ={}
        emptyFor = False
        if len(spreadStatements[line]) == 3:
            emptyFor = False
        else:
            emptyFor = True
        for statements in spreadStatements[line]:
            if not emptyFor:
                if "int " in statements or "long " in statements or "double " in statements or " = " in statements:
                    finalStatementOrder[0]=statements
                elif "for" in statements:
                    finalStatementOrder[1]=statements
                elif "++" in statements or "--" in statements or "-=" in statements or "+=" in statements  or "/=" in statements:
                    finalStatementOrder[2]=statements
                else:
                    print("IS THIS PART OF FOR? "+statements)
            else:    # for cases like: for( ; ; )
                if "   ;" in statements:
                    finalStatementOrder[0] =  statements
                    finalStatementOrder[2] =  statements
                if "for" in statements:
                    finalStatementOrder[1] = statements

        statementsToBeCompiled[line] = finalStatementOrder

    # for k,v in statementsToBeCompiled.items():
    #     print(k,v)
    # print(statementsToBeCompiled['45'])
    linesToReplaceWith={}
    nodesToReplace={}
    searchBy=""
    for line, statements in statementsToBeCompiled.items():
        nodeToInsert = statements[0].split(";;")[0].strip()
        # print(statements)
        leftEnd = "  "+nodeToInsert+"  [label=\""+line+":"
        rightEnd = "\"];\n"
        firstPart = statements[0].split(";;")[1]
        secondPart = statements[1].split(";;")[1]
        nodeToRemove1 = statements[1].split(";;")[0].strip()
        thirdPart = statements[2].split(";;")[1]
        nodeToRemove2 = statements[2].split(";;")[0].strip()
        nodesToReplace[nodeToRemove1]=nodeToInsert
        nodesToReplace[nodeToRemove2]=nodeToInsert

        statement = secondPart.replace("(","("+firstPart+" ; ").replace(")"," ; "+thirdPart+")")
        CFG_statement = leftEnd+statement+rightEnd
        linesToReplaceWith["  [label=\""+line]=CFG_statement
        # print(linesToReplaceWith)
        # break
    #

    # for k,v in nodesToReplace.items():
    #     print(k,v)
    '''
    read the dot file again and find the node and edge section
    '''
    fileContentStream = open(file,'r')
    fileContent= fileContentStream.readlines()
    fileContentStream.close()
    newFileContent=""
    graphEdges =[]
    graphNodes =[]
    for line in fileContent:
        searchWord = "digraph "+fileName+"_CFG {"
        if(searchWord in line):
            verticesFound = True
        if("  // graph-edges" in line):
            edgesFound = True
            verticesFound = False
        if verticesFound:
            graphNodes.append(line)
        if edgesFound:
            graphEdges.append(line)

    startRemoval=[]
    # for k,v in linesToReplaceWith.items():
    #     print(k,v)
    '''
    write the node portion
    '''
    for line in graphNodes:
        # if "endif" in line:
        #     continue
        # else:
        contentFound=False;
        # print(newFileContent,"---------------"+line)
        for searchFactor, replacementStmt in linesToReplaceWith.items():
            # print(searchFactor,replacementStmt,"------")
            if searchFactor in line:
                contentFound=True
                if searchFactor not in startRemoval:
                    newFileContent = newFileContent+replacementStmt
                    startRemoval.append(searchFactor)
                else:
                    newFileContent=newFileContent
                # newFileContent=newFileContent+line
                break
        if(not contentFound):
            newFileContent=newFileContent+line

    # print(newFileContent)

    # skipLine=False
    '''
    write the edge portion
    '''
    for line in graphEdges:
        lineToAdd=""
        # containsIf = False
        #
        # if skipLine:
        #     skipLine = False
        #     containsIf = True
        #     continue


        # for replaceThisNode, insertThisNode in ifReplacements.items():
        #     if replaceThisNode in line and not containsIf:
        #         containsIf = True
        #         skipLine = True
        #         lineToAdd = line.replace(replaceThisNode,insertThisNode)
        #         line=lineToAdd
        #         break
        #         print(line)
        # if(not containsIf):
        if nodesToReplace:
            for replaceThisNode, insertThisNode in nodesToReplace.items():

                if replaceThisNode in line:
                    lineToAdd = line.replace(replaceThisNode,insertThisNode)
                    line=lineToAdd
                else:
                    lineToAdd =line
            if lineToAdd not in newFileContent:
                if(" -> " in lineToAdd):
                    nodes=lineToAdd.strip().strip(";").split(" -> ")
                    if nodes[0] != nodes[1]:
                        newFileContent=newFileContent+lineToAdd
                    else:
                        newFileContent=newFileContent
                else:
                    newFileContent=newFileContent+lineToAdd
        else:
            newFileContent=newFileContent+line



    '''
    save the new dot file
    '''
    with open(file, "w") as writing_file:
        writing_file.write(newFileContent)








if __name__=='__main__':
    main()
