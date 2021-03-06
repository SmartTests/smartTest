#!/bin/bash
# Argument of this script is qualified path of the java package and the original and edited folder name
#Example: python3 comparator.py /Users/kesina/eclipse-workspace/thermostat/src/main/java/com/thermostat/maven/smartProject  27-04-2020_17_01_08 27-04-2020_17_01_08

packageName=$1
originalVersion=$2
newVersion=$3
testRun=0

# IFS='src'
# read -ra PROJECT <<< "$packageName"
# projectDir="${PROJECT[0]}"
# echo $projectDir"---------DD----------"

testDir=${packageName/main/test}

for testFile in "$testDir"/*
do
echo "$testFile"
srcFilePath=${testFile/test/main}
srcFilePath=${srcFilePath/TestIT/}


IFS='/' # forward slash (/) is set as delimiter
read -ra SRCFILE <<< "$srcFilePath" # entry is read into an array as tokens separated by IFS
srcFile=${SRCFILE[${#SRCFILE[@]}-1]}   #srcFile = "${SRCFILE[-1]}" # access last element of array in bash 4.1 and above


IFS='.'
read -ra SRCFILENAME <<< "$srcFile"
srcFileName="${SRCFILENAME[0]}"
IFS=' ' # reset to default value after usage




(python3 comparator.py $srcFileName ../output/$originalVersion ../output/$newVersion || echo "Comparison unsuccessful!") && echo "Comparison complete"


done
