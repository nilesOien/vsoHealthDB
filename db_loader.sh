#!/bin/bash

# Bash script to drive creation of the sqlite database from CSV files.
# Needs the path to the files as an argument.

source pyEnv/bin/activate

if [ "$#" -ne 1 ]
then
 echo A directory with CSV files must be specified
 exit -1
fi

csvDir="$1"

if [ ! -d "$csvDir" ]
then
 echo Directory $csvDir not found
 exit -1
fi

if [ ! -f report.db ]
then
 ./createDB.py
fi

nf=0
for file in "$csvDir"/*.csv
do

 if [ ! -f "$file" ]
 then
  continue
 fi

 ./fileToDB.py --inFile "$file"
 nf=`expr "$nf" + 1`

done

echo $nf CSV files considered

exit 0

