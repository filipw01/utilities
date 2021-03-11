import os

import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.job_loader import JobLoader


class IndeedLoader(JobLoader):
    def __init__(self):
        super().__init__()
        self.region = ""
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def scrape_page(region, job_type, page_number):
        job_type = job_type.replace(' ', '+')
        domain = 'https://indeed.com/jobs'
        if region != "us":
            domain = f'https://{region}.indeed.com/jobs'
        req = requests.get(
            f'{domain}'
            f'?q={job_type}'
            f'&sort=date'
            f'&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11'
            f'&start={page_number}0')

        soup = BeautifulSoup(req.text, features='html.parser')
        return soup.find_all(class_='jobsearch-SerpJobCard')

    def scrape(self):
        self.offers = []
        for region in ["uk", "ca", "de", "us"]:
            self.region = region
            for page in range(1, 4):
                offer_list = IndeedLoader.scrape_page(region, 'full stack', page)
                self.offers += list(map(self.offer_from_tag, offer_list))
            for page in range(1, 4):
                offer_list = IndeedLoader.scrape_page(region, 'front end', page)
                self.offers += list(map(self.offer_from_tag, offer_list))

        all_offers_count = len(self.offers)
        (self.offers, non_remote, old, boring) = self.filter_jobs()
        print(f'Indeed: Scraped {len(self.offers)}/{all_offers_count}')
        print(f'{"":8}Omitted {len(old) + len(non_remote)} jobs:')
        print(f'{"":16}{len(old)} old')
        print(f'{"":16}{len(non_remote)} non-remote')
        print(f'{"":16}{len(boring)} boring')

    def filter_jobs(self):
        result = []
        non_remote = []
        old = []
        boring = []
        boring_techs = ['php', '.net', 'c#', 'angular', 'senior', 'wordpress', 'sr.', 'lead', 'back-end',
                        'project manager', 'java ', 'devops', 'head of']
        old_job_titles = self.get_past_job_titles()

        for job in self.offers:
            if job['title'] in old_job_titles:
                old.append(job)
            elif not job['remote']:
                non_remote.append(job)
            else:
                for boring_tech in boring_techs:
                    if boring_tech in job['title'].lower():
                        boring.append(job)
                        break
                else:
                    result.append(job)

        return result, non_remote, old, boring

    def prepare_email_content(self):
        mail = '<h2>Indeed</h2>'
        for offer in self.offers:
            mail += f'''
            <a href='{offer['href']}'>
                {offer['title']} {offer['salary']} in {offer['location']}
            </a>
            '''
        return mail

    @staticmethod
    def salary_normalizer(salary):
        if salary == 'Error':
            return None
        multiplier = 1
        salary = salary.replace(',', '').replace('a month', '').replace('From', '').replace('Up to', '') \
            .replace('pro Jahr', 'a year').replace('pro Tag', 'a day').replace('pro Stunde', 'an hour')
        if 'a year' in salary:
            multiplier /= 12
            salary = salary.replace('a year', '')
        if 'a day' in salary:
            multiplier *= 23
            salary = salary.replace('a day', '')
        if 'an hour' in salary:
            multiplier *= 160
            salary = salary.replace('an hour', '')
        if '$' in salary:
            multiplier *= 3.8
            salary = salary.replace('$', '')
        if '€' in salary:
            multiplier *= 4.5
            salary = salary.replace('€', '')
        if '£' in salary:
            multiplier *= 5.3
            salary = salary.replace('£', '')
        if multiplier != 1:
            salary_range = [round(float(x) * multiplier, -3) for x in salary.split(' - ')]
            if len(salary_range) == 2:
                return f'{salary_range[0]:,}PLN - {salary_range[1]:,}PLN monthly'
            else:
                return f'{salary_range[0]:,}PLN'
        return salary

    def offer_from_tag(self, tag):
        position = tag.find(class_='jobtitle').text.strip()
        company = getattr(tag.find(class_='company'), 'text', 'Error').strip()
        location = tag.find(class_='location').text.strip()
        remote = getattr(tag.find(class_='remote'), 'text', 'Error').strip()
        salary = getattr(tag.find(class_='salaryText'), 'text', 'Error').strip()
        href = self.absolute_link(tag.find(class_='jobtitle')['href'])
        return {
            'href': href,
            'title': f'{position} {company}',
            'remote': remote == 'Remote' or remote == 'Homeoffice',
            'location': location,
            'salary': IndeedLoader.salary_normalizer(salary),
        }

    def absolute_link(self, link: str):
        if link.startswith('/'):
            if self.region == "us":
                return f'https://indeed.com{link}'
            return f'https://{self.region}.indeed.com{link}'
        return link
