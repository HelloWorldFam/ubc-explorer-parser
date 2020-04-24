import json
import os
import re

# Script for putting file data into array
# https://pastebin.com/trCTwA6U
# https://kaijento.github.io/2017/04/09/python-convert-a-text-file-into-a-dict/

directory = '/Users/scottking/Documents/req/data/ubc/2018/courses'
jsonOut = '/Users/scottking/Documents/req/data/ubc/2018/json-output'

courses_array = []
course = {}

def scriptFile():
    newfile = open(jsonOut + '/' + "output.json", "w")
    for file in os.listdir(directory):
        f = open(directory + '/' + str(file), "r")

        for line in f:
            if len(line) > 3:
                key, value = line.rstrip().split(': ', 1)
                course[key] = value.strip()

            else:
                if course:
                    courses_array.append(course.copy())
                course.clear()
                continue

    newfile.write(json.dumps(courses_array))
    newfile.close()  # close the file after we are done writing


codes = []

def creditsToInt():
    f = open(jsonOut + "/" + "output.json", "r")
    data = json.load(f)
    for course in data:
        if "cred" in course and len(course["cred"]) == 1:
            course["cred"] = int(course["cred"])
        else:
            course["cred"] = None
        codes.append(course["dept"])
    f.close()
    res = open(jsonOut + "/" + "output.json", "w")
    res.write(json.dumps(data))
    res.close()


codeSet = set()
deptJson = {}
deptArray = []

def deptCodesJson():
    for dept in codes:
        codeSet.add(dept)

    array = []
    for code in codeSet:
        array.append(code)
    
    array.sort()

    for dept in array:
        deptJson["dept"] = dept
        deptArray.append(deptJson.copy())
        deptJson.clear()
    newfile = open(jsonOut + '/' + "depts.json", "w")
    newfile.write(json.dumps(deptArray))


def parsePrereqs():
    f = open(jsonOut + "/" + "output.json", "r")
    data = json.load(f)

    for course in data:
        if "preq" in course:
            course["preq"] = re.findall(r'[A-Z]*\s\d{3}', course["preq"])
        if "creq" in course:
            course["creq"] = re.findall(r'[A-Z]*\s\d{3}', course["creq"])

    f.close()
    res = open(jsonOut + "/" + "parsed.json", "w")
    res.write(json.dumps(data))
    res.close()
    
# # call to method
scriptFile()
creditsToInt()
deptCodesJson()
parsePrereqs()