from bs4 import BeautifulSoup
import urllib.request
import concurrent.futures
import json
import re


class Scraper:
    def __init__(self) -> None:
        self.base_url = "https://www.calendar.ubc.ca/vancouver/courses.cfm?page=code"
        self.courses_url = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course"

    def __process_dept(self, link):
        result = []
        html = urllib.request.urlopen(f"{self.base_url}/{link}")
        soup = BeautifulSoup(html, features="html.parser")
        courses = soup.find('dl', {'class': 'double'})

        new_course = {}

        for details in courses.find_all(['dt', 'dd']):
            text = details.text
            split = text.split(" ")
            if details.name == 'dt':
                new_course['dept'] = split[0]
                new_course['code'] = f"{split[0]} {split[1]}"
                new_course['cred'] = split[2][1:-1]
                new_course['link'] = f"{self.courses_url}&dept={split[0]}&course={split[1]}"
            elif details.name == 'dd':
                new_course['desc'] = text.split("\n")[0].strip()

                if 'Prerequisite:' in text:
                    prereqs = text.split('Prerequisite:')[
                        1].split('Corequisite:')[0]
                    new_course['prer'] = prereqs.strip()
                    new_course['preq'] = self.__parse_reqs(prereqs)

                if 'Corequisite:' in text:
                    coreqs = text.split('Corequisite:')[1]
                    new_course['crer'] = coreqs.strip()
                    new_course['creq'] = self.__parse_reqs(coreqs)

                if int(new_course['code'].split(" ")[1]) < 500:
                    result.append(new_course.copy())
                new_course.clear()

        return result

    def __parse_reqs(self, blurb):
        return re.findall(r"\b[A-Z]{3,4} \d{3}\b", blurb.strip())

    def main(self):
        html = urllib.request.urlopen(self.base_url)
        soup = BeautifulSoup(html, features="html.parser")
        table = soup.find('table')
        # links = set([e.attrs['href']
        #              for e in table.find_all('a') if 'href' in e.attrs])
        dept_links = sorted(list(set([e.attrs['href']
                                 for e in table.find_all('a') if 'href' in e.attrs])))

        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(self.__process_dept, list(dept_links))
            # results = executor.map(self.__create_thread, [dept_links[74]])  # cpsc
            # results = executor.map(self.__create_thread, [dept_links[1]])  # acam
            for r in results:
                result += r

        with open('output.json', 'w') as file:
            json.dump(result, file)


scraper = Scraper()
scraper.main()
