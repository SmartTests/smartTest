import json,os

'''
Need to change version and fileName for every java class and run before compareStmt.py. Creates reverse mapping from line to node to compare if the output from statement testCoverage
matches the edges in CFG
'''

version="06-08-2020_17_13"
fileName = "DerivativeStructure"
mapping='/Users/kesina/Dropbox/commons-math/output/'+version+'/'+fileName+'-CFGmapping.json'


stmtStream = open (mapping,'r')

statementCoverageInfo = json.load(stmtStream)
stmtStream.close()
# print([statementCoverageInfo])
# print(type(statementCoverageInfo.split("\n\n")[0]))
newMap={}
for data in statementCoverageInfo:
    for node,detail in data.items():
        for name,stmtNum in detail.items():
            newMap[stmtNum]=node
            break
baseDir = os.path.dirname(mapping)
fileName =mapping.split("/")[7].split("-")[0]
with open(baseDir+os.path.sep+fileName+'-TempMapping.json', 'w') as mappingFile:
    todump=[]
    todump.append(newMap)
    json.dump(todump,mappingFile,indent=2)
# print(newMap)
