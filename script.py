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
            course["preq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["preq"])
        if "creq" in course:
            course["creq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["creq"])

    f.close()
    res = open(jsonOut + "/" + "parsed.json", "w")
    res.write(json.dumps(data))
    res.close()

def getDependencies():
    f = open(jsonOut + "/" + "parsed.json", "r")
    data = json.load(f)

    for course in data:
        for course2 in data:
            if "preq" in course2:
                if course["code"] in course2["preq"]:
                    if not "depn" in course:
                        course["depn"] = []
                    course["depn"].append(course2["code"])

    f.close()
    res = open(jsonOut + "/" + "depend.json", "w")
    res.write(json.dumps(data))
    res.close()

def getCodesForDepts():
    depts = open(jsonOut + "/" + "depts.json", "r")
    courses = open(jsonOut + "/" + "parsed.json", "r")

    deptData = json.load(depts)
    courseData = json.load(courses)

    result = []

    for dept in deptData:
        newDept = {}
        newDept["dept"] = dept["dept"]
        newDept["courses"] = []
        for course in courseData:
            if course["dept"] == dept["dept"]:
                newDept["courses"].append(course["code"])
        result.append(newDept.copy())
    
    for dept in result:
        codesOnly = []
        for course in dept["courses"]:
            x = course.split(' ')
            codesOnly.append(x[1])
        dept["courses"] = codesOnly

    res = open(jsonOut + "/" + "deptCodes.json", "w")
    res.write(json.dumps(result))
    res.close()

    
# call to method
scriptFile()
creditsToInt()
deptCodesJson()
parsePrereqs()
# getDependencies()
getCodesForDepts()