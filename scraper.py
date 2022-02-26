from typing import List
from bs4 import BeautifulSoup
import urllib.request
import concurrent.futures
import re


class Scraper:
    def __init__(self) -> None:
        self.base_url = "https://www.calendar.ubc.ca/vancouver/courses.cfm?page=code"
        self.courses_url = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course"

    def __process_dept(self, link) -> List[dict]:
        result = []
        html = urllib.request.urlopen(f"{self.base_url}/{link}")
        soup = BeautifulSoup(html, features="html.parser")
        courses = soup.find("dl", {"class": "double"})

        new_course = {}

        for details in courses.find_all(["dt", "dd"]):
            text = details.text
            split = text.split(" ")
            if details.name == "dt":
                new_course["dept"] = split[0]
                new_course["code"] = f"{split[0]} {split[1]}"
                new_course["cred"] = split[2][1:-1]  # (3) -> 3, (1-6) -> 1-6
                new_course["link"] = f"{self.courses_url}&dept={split[0]}&course={split[1]}"
                new_course["name"] = details.find("b").text
            elif details.name == "dd":
                new_course["desc"] = text.split("\n")[0].strip()

                if "Prerequisite:" in text:
                    prereqs = text.split("Prerequisite:")[1].split("Corequisite:")[0].split("Equivalency:")[0]
                    new_course["prer"] = prereqs.strip()
                    new_course["preq"] = self.__parse_reqs(prereqs)

                if "Corequisite:" in text:
                    coreqs = text.split("Corequisite:")[1].split("Equivalency:")[0]
                    new_course["crer"] = coreqs.strip()
                    new_course["creq"] = self.__parse_reqs(coreqs)

                # skip grad
                if int(new_course["code"].split(" ")[1]) < 500:
                    result.append(new_course.copy())
                new_course.clear()

        return result

    def __parse_reqs(self, blurb) -> List[str]:
        return re.findall(r"\b[A-Z]{3,4} \d{3}\b", blurb.strip())

    def main(self) -> List[dict]:
        html = urllib.request.urlopen(self.base_url)
        soup = BeautifulSoup(html, features="html.parser")
        table = soup.find("table")
        dept_links = set([e.attrs["href"] for e in table.find_all("a") if "href" in e.attrs])

        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.__process_dept, list(dept_links))
            # results = executor.map(self.__process_dept, [list(dept_links)[40]])
            for r in results:
                result += r

        return result
