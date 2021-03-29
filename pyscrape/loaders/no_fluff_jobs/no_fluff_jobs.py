import os

import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.job_loader import JobLoader


class NoFluffJobsLoader(JobLoader):
    def __init__(self):
        super().__init__()
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    def scrape(self):
        req = requests.get('https://nofluffjobs.com/pl/jobs/remote/frontend?criteria=category%3Dfullstack')
        soup = BeautifulSoup(req.text, features='html.parser')
        root = soup.find_all('nfj-postings-list')
        print(root)
        self.offers = []
        for offer_list in root:
            self.offers += list(map(self.offer_from_tag, offer_list.findChildren('a', recursive=False)))
        # TODO: Fix this loader
        all_offers_count = len(self.offers)
        (self.offers, old, boring) = self.filter_jobs()
        print(f'NoFluffJobs: Scraped {len(self.offers)}/{all_offers_count}')
        print(f'{"":13}Omitted {len(old) + len(boring)} jobs:')
        print(f'{"":21}{len(old)} old')
        print(f'{"":21}{len(boring)} boring')

    def filter_jobs(self):
        result = []
        old = []
        boring = []
        old_job_titles = self.get_past_job_titles()
        boring_tech = ['php', '.net', 'angular', 'java', 'ruby on rails', 'wordpress']

        for job in self.offers:
            if job['title'] in old_job_titles:
                old.append(job)
            elif job['technology'] in boring_tech:
                boring.append(job)
            else:
                result.append(job)

        return result, old, boring

    def prepare_email_content(self):
        mail = '<h2>No Fluff Jobs</h2>'
        for offer in self.offers:
            mail += f'''
            <a href='{offer['href']}'>
                {offer['title']} {offer['salary']}
            </a>
            '''
        return mail

    @staticmethod
    def offer_from_tag(tag):
        position = tag.find(class_='posting-title__position').text.strip()
        company = tag.find(class_='posting-title__company').text.strip()
        salary = tag.find(class_='salary').text
        technology = getattr(tag.find('common-posting-item-tag'), 'text', 'Error').strip()
        href = NoFluffJobsLoader.absolute_link(tag['href'])
        return {
            'href': href,
            'title': f'{position} {company}',
            'salary': salary,
            'technology': technology
        }

    @staticmethod
    def absolute_link(link: str):
        if link.startswith('/'):
            return f'https://nofluffjobs.com{link}'
        return link
