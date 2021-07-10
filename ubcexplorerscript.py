import re
from ubcalend_txt import Scraper

class UBCExplorerScript:
    def __get_course_links__(self, course):
        code = course["code"].split(" ")
        course["link"] = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept=" + code[0] + "&course=" + code[1]
        return course

    def __generate_json_array__(self, calendar_data):
        courses_array = []
        course = {}
        codes = []

        for line in calendar_data:
            if len(line) > 3 and line != 'newline':
                key, value = line.rstrip().split(': ', 1)
                course[key] = value.strip()
                
            elif line == 'newline':
                if course:
                    courses_array.append(course.copy())
                course.clear()
                continue

        for course in courses_array:
            if "cred" in course and len(course["cred"]) == 1:
                course["cred"] = int(course["cred"])
            else:
                course["cred"] = None
            
            if "dept" in course:
                codes.append(course["dept"])

        for course in courses_array:
            if "preq" in course:
                course["preq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["preq"])
            if "creq" in course:
                course["creq"] = re.findall(r'[A-Z]*\s\d{3}[A-Z]*', course["creq"])

        for course in courses_array:
            for course2 in courses_array:
                if "preq" in course2:
                    if "code" in course and "preq" in course2 and course["code"] in course2["preq"]:
                        if not "depn" in course:
                            course["depn"] = []
                        course["depn"].append(course2["code"])

        return [self.__get_course_links__(course) for course in courses_array]
        

    def main(self):
        scraper = Scraper()
        calendar_data = scraper.main()
        return self.__generate_json_array__(calendar_data)

