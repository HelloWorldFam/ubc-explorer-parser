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
                new_course["cred"] = self.__credits_to_number(split[2][1:-1])  # (3) -> 3, (1-6) -> 1-6
                new_course["link"] = f"{self.courses_url}&dept={split[0]}&course={split[1]}"
                new_course["name"] = details.find("b").text
            elif details.name == "dd":
                new_course["desc"] = self.__strip(text.split("\n")[0])

                if "Prerequisite:" in text:
                    preq_text = self.__strip(text.split("Prerequisite:")[1].split("Corequisite:")[0].split("Equivalency:")[0])
                    self.__process_reqs(preq_text, new_course, "prer", "preq")

                if "Corequisite:" in text:
                    creq_text = self.__strip(text.split("Corequisite:")[1].split("Equivalency:")[0])
                    self.__process_reqs(creq_text, new_course, "crer", "creq")

                # skip grad
                if int(new_course["code"].split(" ")[1]) < 500:
                    result.append(new_course.copy())
                new_course.clear()

        return result

    def __process_reqs(self, text: str, course: dict, text_label: str, req_label: str) -> List[str]:
        course[text_label] = text
        reqs = re.findall(r"\b[A-Z]{3,4} \d{3}\b", text)
        if len(reqs):
            course[req_label] = reqs

    def __strip(self, text: str):
        return re.sub(r"[ ]{2,}", " ", text).strip()

    def __credits_to_number(self, creds: str):
        if creds.isnumeric():
            return int(creds)
        try:
            num = float(creds)
            return num
        except:
            return None

    def main(self) -> List[dict]:
        html = urllib.request.urlopen(self.base_url)
        soup = BeautifulSoup(html, features="html.parser")
        table = soup.find("table")
        dept_links = set([e.attrs["href"] for e in table.find_all("a") if "href" in e.attrs])

        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.__process_dept, list(dept_links))
            for r in results:
                result += r

        return result
