import os


sourceFileName = 'Gaussian'
extension=".log"



fileContent = []
projectPath = os.path.dirname(os.getcwd())
mutationFileName = "mutants-"+sourceFileName+extension
mutationLogLocation = projectPath+os.path.sep+"mutations"
fileStream = open(mutationLogLocation+os.path.sep+mutationFileName,'r')
fileContent = fileStream.readlines()
fileStream.close()
for num,line in enumerate(fileContent):
    if(num<51):   #find for top 50
        divided = line.split(":")
        mutationNumber = divided[0]
        lineNumber = divided[5]
        print(mutationNumber,":",lineNumber)
