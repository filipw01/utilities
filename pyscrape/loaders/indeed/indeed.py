import os

import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.loader import Loader


class IndeedLoader(Loader):
    def __init__(self):
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    def scrape(self):
        req = requests.get(
            'https://uk.indeed.com/jobs?q=full+stack+developer&sort=date&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11')

        soup = BeautifulSoup(req.text, features='html.parser')
        offer_list = soup.find_all(class_='jobsearch-SerpJobCard')
        offers = list(map(self.offer_from_tag, offer_list))

        old_job_titles = self.get_past_job_titles()
        # include only new offers
        self.offers = list(filter(lambda x: x['title'] not in old_job_titles, offers))
        # exclude non-remote jobs
        self.offers = list(filter(lambda x: x['remote'] == 'Remote', self.offers))

    def prepare_email_content(self):
        mail = '<h2>Indeed</h2>'
        for offer in self.offers:
            mail += f'''
            <a href='{offer['href']}'>
                {offer['title']} {offer['salary']} in {offer['location']}
            </a>
            '''
        return mail

    def post_email(self):
        self.save_scraped_jobs()
        self.remove_old_jobs()

    def get_past_job_titles(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'r') as file:
            return file.read().split('\n')[:-1]

    def save_scraped_jobs(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'a') as file:
            file.writelines('\n'.join(map(lambda x: x['title'], self.offers)) + '\n')

    def remove_old_jobs(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'r+') as file:
            jobs = file.read().split('\n')[:-1]
            last_100_jobs = '\n'.join(jobs[-100:])
            file.seek(0)
            file.truncate()
            file.write(last_100_jobs + '\n')

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
