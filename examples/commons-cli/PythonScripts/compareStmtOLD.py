import json
from collections import defaultdict
version="06-08-2020_11_30"
fileName = "DerivativeStructure"

mapping = '/Users/kesina/Dropbox/commons-math/output/'+version+'/'+fileName+'-TempMapping.json'
stmtFile = '/Users/kesina/Dropbox/commons-math/output/'+fileName+'-StatementsCovered.txt'
req = '/Users/kesina/Dropbox/commons-math/output/'+version+'/'+fileName+'-CFGedgeCoverageRequirements.txt'
jsonMappingDetail = '/Users/kesina/Dropbox/commons-math/output/'+version+'/'+fileName+'-CFGmapping.json'

r = open(req,'r')
r=r.read()

j = open(jsonMappingDetail,'r')
jsonDetail = json.load(j)
trackLine=set()
trackNode =set()
mappingDict={}
m = open(mapping,'r')
maps = json.load(m)
for map in maps:
    for k,v in map.items():
        mappingDict[k]=v

# 111,112
# 112,96
# 112,86
# 112,76
# 112,77
# 112,78
# 112,97
# 112,114
# 112,117
# 112,119
# 62,190
# 62,191
# 62,192
# 62,288
with open(stmtFile,'r') as f:
    fileContent = f.read().split("\n\n")
    for line in fileContent:
        methods = line.split(":")[1].split(";;")
        # print(methods)
        for method in methods:
            edges=method.split("=")[1].replace("[","").replace("]","").split("\n")
            # print(lines)
            for edge in edges:
                node = edge.split(",")
                # print(node)
                try:
                    edgeVal = mappingDict[node[0]]+","+mappingDict[node[1]]
                    # print(edgeVal)
                except:
                    trackLine.add(edge)
                    # trackNode.add(edgeVal)
                    continue
                if edgeVal not in r:
                    stmt = mappingDict[node[0]]+","+mappingDict[node[1]]
                    trackNode.add(stmt)
                    # print("WORKS----------",line)
                    break
print("SIZE---------",len(trackNode))
for line in trackNode:
    print("NO EDGE",line)

connectingNode={}
for line in trackNode:
    startNode = line.split(",")[0]
    endNode = line.split(",")[1]
    searchWith= startNode+","
    listOfReqs = r.split("\n")
    for edgeReq in listOfReqs:
        if searchWith in edgeReq:
            connection = edgeReq.split(",")[1]
            # print(startNode,connection)
            information = [detail for detail in jsonDetail if detail.get(connection)]
            if(information):
                statement = information[0][connection]['statement']
                if 'endfor' in statement or 'endif' in statement:
                     connectingNode[startNode]=connection
# print(connectingNode)

for start, connection in connectingNode.items():
    missingEdge = [line for line in trackNode if start in line][0]
    # print(missingEdge)
    searchForNode = missingEdge.split(",")[1]
    searchForEdge = connection+","+searchForNode
    listOfReqs = r.split("\n")
    founde = [edgeReq for edgeReq in listOfReqs if searchForEdge in edgeReq]
    if(founde):
        founde = founde[0]

        print("-----",start, founde.split(",")[1])
        foundEdge = start+","+founde.split(",")[1]
        trackNode.remove(foundEdge)
            # foundEdge = [edge for edge in edgeReq if searchForEdge in edge]
            # print(foundEdge,"------------")
            # if(foundEdge):
            #     print(start, connection, foundEdge)
    else:
        print(searchForEdge,"NOT FOUND")

for line in trackNode:
    print("NO EDGE",line)


# for line in trackLine:
#     print("NO NODE",line)
