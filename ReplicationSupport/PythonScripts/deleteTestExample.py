import runTest

def main():
    outputFolderCreated="03-10-2020_19_26_37"
    mutatedSource="PolynomialFunction"
    packagePath=projectPath+"/src/main/java/org/apache/commons/math3/analysis/polynomials"
    item=1
    runTest.runTest(outputFolderCreated,mutatedSource,item,packagePath)


if __name__=='__main__':
    main()
