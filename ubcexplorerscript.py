from typing import List
from scraper import Scraper
import json

class UBCExplorerScript:
    # for each course in the course array, search for all instances where the current course is a prereq for another course
    # then adds courses found to the 'depn' array which represents the list of dependencies for that course
    # returns the modified course array
    def __get_dependencies(self, courses_array: List[dict]) -> List[dict]:
        courses_map = {course["code"]:course for course in courses_array}
        courses_with_preqs = [course for course in courses_array if "preq" in course]

        for course in courses_with_preqs:
            for preq in course["preq"]:
                if preq in courses_map and preq != course["code"]:
                    to_update = courses_map[preq]
                    if not "depn" in to_update:
                        to_update["depn"] = set()
                    to_update["depn"].add(course["code"])
                

        for course in courses_map.values():
            if "depn" in course:
                course["depn"] = sorted(list(course["depn"]))
                
        return [value for value in courses_map.values()]

    # generates final list of course objects to be uploaded to mongo
    # returns final course array
    def __generate_json_array(self, calendar_data: List[dict]) -> List[dict]:
        sorted_courses = sorted(calendar_data, key=lambda course: course['code'])
        return self.__get_dependencies(sorted_courses)

    def main(self) -> List[dict]:
        scraper = Scraper()
        calendar_data = scraper.main()
        return self.__generate_json_array(calendar_data)

# testing
# script = UBCExplorerScript()
# output = script.main()
# with open('output.json', 'w') as file:
#     json.dump(output, file)
