#!/bin/bash
# 1. createOutputDirectory.py creates output directory for all the smart test related result.
# Argument of this script is qualified path of the java source code. Example: /Users/kesina/Dropbox/commons-math/src/main/java/org/apache/commons/math4/analysis/changed.java
# Example Kesinas-MBP:PythonScripts kesina$ bash runProgex.sh /Users/kesina/Dropbox/commons-math/src/main/java/org/apache/commons/math4/analysis/FunctionUtils.java original

str=$1
codeVersion=$2
testRun=0

IFS="src"
read -ra PROJECT <<< "$str"
projectDir="${PROJECT[0]}"

IFS='/' # forward slash (/) is set as delimiter
read -ra SRCFILE <<< "$str" # str is read into an array as tokens separated by IFS
srcFile=${SRCFILE[${#SRCFILE[@]}-1]}   #srcFile = "${SRCFILE[-1]}" # access last element of array in bash 4.1 and above

IFS='.'
read -ra SRCFILENAME <<< "$srcFile"
srcFileName="${SRCFILENAME[0]}"
IFS=' ' # reset to default value after usage

python3 sourceCleanUp.py $str
python3 createOutputDirectory.py


cd ../output

#get the most recently created folder in output -U gets the oldest so -Ur to reverse it, head -1 to pick top and cut to remove "/"
recentFile=$(ls -Ur */ | head -1 |cut -d'/' -f1)
echo "OUTPUT FOLDER \""$recentFile"\" created"

cd ../progex-v3.4.5/
java -jar progex.jar -outdir ../output/$recentFile -cfg $1 #../src/main/java/edu/gmu/kbaral/SourceClass.java or Complete path from argument
echo "CFG created for "$srcFile

cd ../PythonScripts/
(python3 graphparser.py $srcFileName ../output/$recentFile || echo "CFG GRAPH COULDN'T BE PARSED!") && echo "CFG GRAPH PARSED SUCCESSFULLY!"

cd ..

if [[ $codeVersion = 'original' ]]
then
  echo $(pwd)
  mvn verify -Drat.skip=true
  testRun=1
fi


cd output
currentDir=pwd
if [[ $testRun -eq 1 ]] && [[ -e "$currentDir/StatementsCovered.txt" ]]
then
  echo "Tests were run successfully and statement coverage was tracked!"
else
  echo "statment coverage wasn't tracked"
  exit 1
fi

cd ../PythonScripts
python3 finalAnalysis.py ../output/$recentFile $srcFileName"-CFGedgeCoverageRequirements.txt" $srcFileName"-CFGmapping.json"
