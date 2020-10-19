import json

inputfile=open('1dotmapping.json','r')

jsondata=json.load(inputfile)
for data in jsondata:
    for k in data:
        if k=='v2':
            print(data)
