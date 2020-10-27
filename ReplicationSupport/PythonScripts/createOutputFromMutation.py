import os, sys
import subprocess
import json
import time
import runTest

def getRelevantData(fileDir,fileName,extension):
    file = os.path.join(fileDir,fileName+extension)

    fileContentStream = open(file,'r')
    fileContent= fileContentStream.readlines()

    fileContentStream.close()
    return fileContent



def main():
    if(len(sys.argv)>1):
        packageName = sys.argv[-3]
        originalVersion = sys.argv[-1]
        mutatedSource = sys.argv[-2]
        totalMutation = sys.argv[-4]
    else:
        print('Example: python3 createOutputFromMutation.py 50 /src/main/java/org/apache/commons/math3/analysis/differentiation DSCompiler  27-04-2020_17_01_08')
        print('Usage: python3 createOutputFromMutation.py <#no> <packageName> <SourceClassName> <originalVersionDir>')
        return
    mutatedFileDir = os.path.abspath(os.getcwd()) #same as the pythonScript
    projectPath = os.path.dirname(os.getcwd())

    packagePath = projectPath+packageName
    sourceExtension=".java"                                              #change this
    mutationFolderPath = projectPath+"/mutations/mutants-"+mutatedSource
    pythonScriptLocation = os.getcwd()
    storeOutputResult ={}
    mutationCompleted=False


    #for each mutation, create a new source copy and run runProgex.sh on that version
    startTime=time.time()
    # comparisonFolderLocation = pythonScriptLocation+os.path.sep+"comparisonResult"+os.path.sep+"comparisonResult-"+mutatedSource
    # os.mkdir(comparisonFolderLocation)
    totalMutation= int(totalMutation)+1
    print(packagePath+os.path.sep+mutatedSource)

    for item in range(1,totalMutation):
        mutationCompleted = False
        fileContent=""
        try:
            os.chdir(mutationFolderPath)
            print("ANALYSIS OF MUTATION================",item)
            for root, dir, fileNames in os.walk(str(item)):
                if not fileNames:
                    continue
                if sourceExtension in fileNames[0]:
                    mutatedProgramFile = mutationFolderPath+os.path.sep+root+os.path.sep+fileNames[0]
                    with open(mutatedProgramFile,"r") as readFile:
                        fileContent = readFile.read()
                    with open(packagePath+os.path.sep+mutatedSource+sourceExtension,"w") as writeFile:
                        writeFile.write(fileContent)
                    mutationCompleted = True

            if mutationCompleted:
                os.chdir(pythonScriptLocation)
                runAnalysis = "bash temprunProgex.sh "+packagePath+os.path.sep+mutatedSource
                print(runAnalysis,"PROGEX")
                #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL added to suppress output
                subprocess.run(runAnalysis,shell=True, check=True)#,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                outputFolderCreated = getRelevantData(mutatedFileDir,"newFolderTracker",".txt")[0].strip("\n")
                storeOutputResult[item]=mutatedSource+"-"+outputFolderCreated+".json"

                storeComparisonLog = " > comparisonResult/"+"comparisonResult-"+mutatedSource+"/"+"ComparisonResult-"+outputFolderCreated+".txt"
                # print(projectPath)
                # print(packageName)
                # print(originalVersion)
                # print(outputFolderCreated)
                # print(storeComparisonLog)
                comparisonScript="bash tempcompareCoverage.sh "+ packagePath+os.path.sep+mutatedSource+" "+originalVersion+" "+outputFolderCreated#+storeComparisonLog
                # print(comparisonScript,"------------------")

                subprocess.run(comparisonScript,shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Comparison Done")
                runTest.runTest(outputFolderCreated,mutatedSource,item,packagePath)
                # rerunTest = "python3 runTest.py "+mutatedSource+" "+outputFolderCreated
                # subprocess.run(rerunTest,shell=True, check=True)


        except subprocess.CalledProcessError as e:
            print("ERROR on mutation",item, e)

    if mutationCompleted:
        outputJsonFile = "outputOfProgexOnMutated.json"
        with open(projectPath+os.path.sep+outputJsonFile, 'w') as mappingFile:
            json.dump(storeOutputResult,mappingFile,indent=2)
            print("Output saved")
        timeDif = time.time()-startTime
        print("==================TIME TAKEN FOR ANALYSIS========================",timeDif)
    else:
        print("ANALYSIS SKIPPED FOR MUTATION ",item,"================")

if __name__=='__main__':
    main()
