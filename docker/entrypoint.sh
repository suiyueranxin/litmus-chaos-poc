#!/bin/bash

# echo "Start chaos test..."
CASE_FILE_NAME=$1
KEYWORD=$2
if (python -m unittest discover -s ${RUN_PATH} -p ${CASE_FILE_NAME} -k ${KEYWORD}) then
    RESULT=PASS
else
    RESULT=FAIL
fi
echo ${RESULT}
# tail -f /dev/null