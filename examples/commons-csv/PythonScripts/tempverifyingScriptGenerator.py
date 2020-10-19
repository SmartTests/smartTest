import sys, os
import json
from collections import defaultdict
from difflib import SequenceMatcher
import subprocess
import itertools

class Verifier:
    def __init__(self):
        self.recordWork=''

    def convertJsonToDict(self,jsonMapping):
        mappingDict = dict()
        print(type(jsonMapping))
        for data in jsonMapping:
            for k,v in data.items():
                mappingDict[k]=v
        return mappingDict

    def getRelevantData(self,fileDir,fileName):
        file = os.path.join(os.path.abspath(fileDir),fileName)

        fileContentStream = open(file,'r')
        if ".json" in fileName:
            fileContent = json.load(fileContentStream)
        else:
            fileContent = fileContentStream.readlines()
        fileContentStream.close()
        return fileContent

def main():
    if(len(sys.argv)>1):
        originalVersion = sys.argv[-1]
        sourceFileName = sys.argv[-2]
        packageName = sys.argv[-3]
        totalMutation = sys.argv[-4]
        verifier = Verifier()
    else:
        print('Example: python3 verifyingScriptGenerator.py function Logistic 25-09-2020_16_11_02')
        print('Usage: python3 verifier.py <packageName> <sourceFileName> <originalVersion>')
        return

    projectPath = os.path.dirname(os.getcwd())
    mutationAnalysisLog = " > ../logs/mutationAnalysisLog-"+sourceFileName+".log"  #To check time taken or any possible error
    if packageName !="x":
        createOutputScript = "python3 tempcreateOutputFromMutation.py "+totalMutation+" /src/main/java/org/apache/commons/csv"+os.path.sep+packageName+" "+sourceFileName+" "+originalVersion+mutationAnalysisLog
    else:
        createOutputScript = "python3 tempcreateOutputFromMutation.py "+totalMutation+" /src/main/java/org/apache/commons/csv"+" "+sourceFileName+" "+originalVersion+mutationAnalysisLog
    print(createOutputScript,"createOutputScript")
    subprocess.run(createOutputScript,shell=True, check=True)
    mutationOutputMappingData = verifier.getRelevantData(projectPath,"outputOfProgexOnMutated.json")
    mutationLines = verifier.getRelevantData(projectPath+os.path.sep+"mutations","mutants-"+sourceFileName+".log")
    mutationDict = {}
    totalMutation = int(totalMutation)+1
    for num,line in enumerate(mutationLines):
        if(num<totalMutation):   #find for top 50
            divided = line.split(":")
            mutationNumber = divided[0]
            lineNumber = divided[5]
            mutationDict[mutationNumber] = lineNumber

    # print(mutationOutputMappingData)
    mutationOutputMappingDict = mutationOutputMappingData#verifier.convertJsonToDict(mutationOutputMappingData)
    verificationLog = " >> ../logs/verificationLog.log"  #To check verification result

    for k,file in mutationOutputMappingDict.items():
        if k in mutationDict:
            createVerifierScript = "python3 verifier.py "+file+" "+mutationDict[k]+verificationLog
            print(createVerifierScript,"createVerifierScript")

            subprocess.run(createVerifierScript,shell=True, check=True)

    #/Users/kesina/Dropbox/SmartTestVerification/majorGeneratedData/function/HarmonicOscillator/
    DestinationToSave = "/Users/kesina/Dropbox/SmartTestVerification/majorGeneratedData"+os.path.sep+packageName+os.path.sep+sourceFileName+os.path.sep
    # sourceOfComparisonResultFiles = "comparisonResult"+os.path.sep+"comparisonResult-"+sourceFileName+os.path.sep
    # copyComparisonResult = "mv "+sourceOfComparisonResultFiles+" "+DestinationToSave
    # print(copyComparisonResult,"copyComparisonResult")
    # subprocess.run(copyComparisonResult,shell=True, check=True)
    sourceOfProgex = "../outputOfProgexOnMutated.json"
    copyProgexResult = "mv "+sourceOfProgex+" "+DestinationToSave
    print(copyProgexResult,"copyProgexResult")
    subprocess.run(copyProgexResult,shell=True, check=True)
    createNewProgexFile = "touch ../outputOfProgexOnMutated.json"
    print(createNewProgexFile,"createNewProgexFile")
    subprocess.run(createNewProgexFile,shell=True, check=True)
    createNewOutputDir = "mkdir ../output/output"
    print(createNewOutputDir,"createNewOutputDir")

    subprocess.run(createNewOutputDir,shell=True, check=True)

    moveFileToNewOutputDir = "mv ../output/09-*/ ../output/output/" # change everyday
    print(moveFileToNewOutputDir,"moveFileToNewOutputDir")

    subprocess.run(moveFileToNewOutputDir,shell=True, check=True)

    moveOutput = "mv ../output/output"+" "+DestinationToSave
    print(moveOutput,"makeFinalForSource")

    subprocess.run(moveOutput,shell=True, check=True)
    makeFinalForSource = "mkdir ../finalResult/finalResult-"+sourceFileName
    print(makeFinalForSource,"makeFinalForSource")
    subprocess.run(makeFinalForSource,shell=True, check=True)

    # makeFinalForOthers= "mkdir ../finalResult/finalResult-others"
    # print(makeFinalForOthers,"makeFinalForOthers")
    #
    # subprocess.run(makeFinalForOthers,shell=True, check=True)

    moveSourceFinal = "mv ../finalResult/"+sourceFileName+"* ../finalResult/finalResult-"+sourceFileName
    print(moveSourceFinal,"moveSourceFinal")

    subprocess.run(moveSourceFinal,shell=True, check=True)

    # moveOtherFinal = "mv ../finalResult/*.json ../finalResult/finalResult-others/"
    # print(moveOtherFinal,"moveOtherFinal")
    #
    # subprocess.run(moveOtherFinal,shell=True, check=True)

    relocateFinals = "mv ../finalResult/finalResult-"+sourceFileName+" "+DestinationToSave
    print(relocateFinals,"relocateFinals")

    subprocess.run(relocateFinals,shell=True, check=True)
















if __name__=='__main__':
    main()
