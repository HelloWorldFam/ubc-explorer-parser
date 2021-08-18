import re
from typing import List
from ubcalend_txt import Scraper

class UBCExplorerScript:
    # converts output from ubcalend_txt script to list of dicts
    # returns list of dicts (json array) that represent courses
    def __convert_calend_data_to_dict(self, calendar_data: List[str]) -> List[dict]:
        courses_array = []
        course = {}

        for line in calendar_data:
            if len(line) > 3 and line != 'newline':
                key, value = line.rstrip().split(': ', 1)
                course[key] = value.strip()
                
            elif line == 'newline':
                if course:
                    courses_array.append(course.copy())
                course.clear()
                continue
        
        return courses_array


    # for a given course, converts the credits value from string to integer
    # returns the modified course
    def __credits_to_int(self, course: dict) -> dict:
        if "cred" in course and len(course["cred"]) == 1:
            course["cred"] = int(course["cred"])
        else:
            course["cred"] = None
        return course


    # converts a given course's prereq/coreq description into a list of course codes
    # returns the modified course
    def __parse_prereqs(self, course: dict) -> dict:
        if "preq" in course:
            course["preq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["preq"])
        if "creq" in course:
            course["creq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["creq"])
        return course


    # for each course in the course array, search for all instances where the current course is a prereq for another course
    # then adds courses found to the 'depn' array which represents the list of dependencies for that course
    # returns the modified course array
    def __get_dependencies(self, unprocessed: List[dict]) -> List[dict]:
        courses_array = unprocessed.copy()
        for course in courses_array:
            for course2 in courses_array:
                if "preq" in course2:
                    if "code" in course and "preq" in course2 and course["code"] in course2["preq"]:
                        if not "depn" in course:
                            course["depn"] = []
                        course["depn"].append(course2["code"])
        return courses_array


    # attaches a link to the SSC course page to each of the courses
    # returns the modified course
    def __get_course_links(self, course: dict) -> dict:
        code = course["code"].split(" ")
        course["link"] = f"https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept={code[0]}&course={code[1]}"
        return course


    # generates final list of course objects to be uploaded to mongo
    # returns final course array
    def __generate_json_array(self, calendar_data: List[str]) -> List[dict]:
        courses_array = self.__convert_calend_data_to_dict(calendar_data)
        courses_array = [self.__credits_to_int(course) for course in courses_array]
        courses_array = [self.__parse_prereqs(course) for course in courses_array]
        courses_array = self.__get_dependencies(courses_array)
        return [self.__get_course_links(course) for course in courses_array]
        

    def main(self) -> List[dict]:
        scraper = Scraper()
        calendar_data = scraper.main()
        return self.__generate_json_array(calendar_data)

