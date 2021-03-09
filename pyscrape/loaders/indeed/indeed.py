import os

import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.job_loader import JobLoader


class IndeedLoader(JobLoader):
    def __init__(self):
        super().__init__()
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    def scrape(self):
        req = requests.get(
            'https://uk.indeed.com/jobs?q=full+stack+developer&sort=date&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11')

        soup = BeautifulSoup(req.text, features='html.parser')
        offer_list = soup.find_all(class_='jobsearch-SerpJobCard')
        self.offers = list(map(self.offer_from_tag, offer_list))

        all_offers_count = len(self.offers)
        (self.offers, non_remote, old) = self.filter_jobs()
        print(f'Indeed: Scraped {len(self.offers)}/{all_offers_count}')
        print(f'{"":8}Omitted {len(old) + len(non_remote)} jobs:')
        print(f'{"":16}{len(old)} old')
        print(f'{"":16}{len(non_remote)} non-remote')

    def filter_jobs(self):
        result = []
        non_remote = []
        old = []
        old_job_titles = self.get_past_job_titles()

        for job in self.offers:
            if job['title'] in old_job_titles:
                old.append(job)
            elif job['remote'] != 'Remote':
                non_remote.append(job)
            else:
                result.append(job)

        return result, non_remote, old

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
    def offer_from_tag(tag):
        position = tag.find(class_='jobtitle').text.strip()
        company = tag.find(class_='company').text.strip()
        location = tag.find(class_='location').text.strip()
        remote = getattr(tag.find(class_='remote'), 'text', 'Error').strip()
        salary = getattr(tag.find(class_='salaryText'), 'text', 'Error').strip()
        href = IndeedLoader.absolute_link(tag.find(class_='jobtitle')['href'])
        return {
            'href': href,
            'title': f'{position} {company}',
            'remote': remote,
            'location': location,
            'salary': salary,
        }

    @staticmethod
    def absolute_link(link: str):
        if link.startswith('/'):
            return f'https://uk.indeed.com{link}'
        return link
