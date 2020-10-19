#!/bin/bash
# 1. createOutputDirectory.py creates output directory for all the smart test related result.
# Argument of this script is qualified path of the java package and the word original or edited
#Example: /Users/kesina/eclipse-workspace/thermostat/src/main/java/com/thermostat/maven/smartProject

packageName=$1
codeVersion=$2
testRun=0

# IFS='src'
# read -ra PROJECT <<< "$packageName"
# projectDir="${PROJECT[0]}"
# echo $projectDir"---------DD----------"

python3 createOutputDirectory.py > newFolderTracker.txt
recentFile=$(head -n 1 newFolderTracker.txt)
# cd ../output
#
# #get the most recently created folder in output -U gets the oldest so -Ur to reverse it, head -1 to pick top and cut to remove "/"
# recentFile=$(ls -Ur */ | head -1 |cut -d'/' -f1)
# if [[ $recentFile == "" ]]
# then
# recentFile=$(ls -Ur | head -1 |cut -d'/' -f1)
# fi
# if [[ $recentFile == '10-08-2020_09_22' ]]
# then
# recentFile=$(ls -Ur */ | head -1 |cut -d'/' -f1)
# fi
echo "OUTPUT FOLDER \""$recentFile"\" created"



cd ..



#testFile=${packageName/main/test} #replace "main" with "test"

# for testFile in "$testDir"/*         #do all steps for each test class in the directory
# do
echo "$packageName"
#srcFilePath=${testFile/test/main}
srcFilePath=${packageName}.java


IFS='/' # forward slash (/) is set as delimiter
read -ra SRCFILE <<< "$srcFilePath" # entry is read into an array as tokens separated by IFS
srcFile=${SRCFILE[${#SRCFILE[@]}-1]}   #srcFile = "${SRCFILE[-1]}" # access last element of array in bash 4.1 and above


IFS='.'  #remove .java
read -ra SRCFILENAME <<< "$srcFile"
srcFileName="${SRCFILENAME[0]}"
IFS=' ' # reset to default value after usage

if [[ $codeVersion = 'original' ]] #run testclass separately
then
  #split by java
  delimiter="java/"
  string=$1$delimiter

  #Split the text based on the delimiter
  myarray=()
  while [[ $string ]]; do
    myarray+=( "${string%%"$delimiter"*}" )
    string=${string#*"$delimiter"}
  done

  testClassName=${myarray[1]}'/'$srcFileName'TestIT'
  echo "============RUNNING TEST============="$testClassName
  mvn -Dit.test=$testClassName verify -Drat.skip=true -q
  testRun=1
fi


#echo "==============H?ere=================$(pwd)"
cd progex-v3.4.5/
java -jar progex.jar -outdir ../output/$recentFile -cfg $srcFilePath >> progexLog.txt
#../src/main/java/edu/gmu/kbaral/SourceClass.java or Complete path from argument
echo "=================CFG created for "$srcFile

cd ../PythonScripts/
(python3 cleanupDot.py $srcFileName ../output/$recentFile || echo "DOT FILE NOT CLEANED") && echo "DOT FILE SUCCESSFULLY CLEAN!!"
(python3 graphparser.py $srcFileName ../output/$recentFile || echo "CFG GRAPH COULDN'T BE PARSED!") && echo "CFG GRAPH PARSED SUCCESSFULLY!"




cd ../output
currentDir=$(pwd)
if [[ $testRun -eq 1 ]] && [[ -e "$currentDir/$srcFileName-StatementsCovered.txt" ]] && [[ $codeVersion == 'original' ]]
then
  stateCoverageTracked=1
  echo "Tests were run successfully and statement coverage was tracked!"
elif [[ $testRun -eq 1 ]] && [[ ! -e "$currentDir/$srcFileName-StatementsCovered.txt" ]]
then
  echo "Unable to track statement coverage. Something went wrong! please check "
  exit 1
else
  echo "Statement coverage wasn't tracked."
fi

if [[ $codeVersion == 'original' ]] && [[ $stateCoverageTracked -eq 1 ]]
then
  cd ../PythonScripts
  python3 testRequirementMapper.py ../output/$recentFile $srcFileName

#  python3 testRequirementMapper.py ../output/$recentFile $srcFileName"-CFGedgeCoverageRequirements.txt" $srcFileName"-CFGmapping.json"
  echo $srcFileName"-SmartTestData.json created!"
else
  echo "SmartTest mapping not created."
fi
cd ..


