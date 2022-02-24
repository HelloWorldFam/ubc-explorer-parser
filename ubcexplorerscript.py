from typing import List
from scraper import Scraper
import json

class UBCExplorerScript:
    # for a given course, converts the credits value from string to integer
    # returns the modified course
    def __credits_to_int(self, course: dict) -> dict:
        if "cred" in course and len(course["cred"]) >= 1 and course["cred"].isnumeric():
            course["cred"] = int(course["cred"])
        else:
            course["cred"] = None
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
        for course in courses_array:
            if "depn" in course:
                course["depn"] = sorted(course["depn"])
        return courses_array

    # generates final list of course objects to be uploaded to mongo
    # returns final course array

    def __generate_json_array(self, calendar_data: List[dict]) -> List[dict]:
        courses_array = calendar_data
        courses_array = sorted([self.__credits_to_int(course) for course in courses_array], key=lambda course: course['code'])
        return self.__get_dependencies(courses_array)

    def main(self) -> List[dict]:
        scraper = Scraper()
        calendar_data = scraper.main()
        return self.__generate_json_array(calendar_data)

# testing
script = UBCExplorerScript()
output = script.main()
with open('output.json', 'w') as file:
    json.dump(output, file)