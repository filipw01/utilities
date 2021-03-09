import os

import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.loader import Loader


class NoFluffJobsLoader(Loader):
    def __init__(self):
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    def scrape(self):
        req = requests.get('https://nofluffjobs.com/pl/jobs/remote/frontend?criteria=category%3Dfullstack')

        soup = BeautifulSoup(req.text, features='html.parser')
        root = soup.find_all('nfj-postings-list')
        offers = []
        for offer_list in root:
            offers += list(map(self.offer_from_tag, offer_list.findChildren('a', recursive=False)))

        old_job_titles = self.get_past_job_titles()
        # include only new offers
        self.offers = list(filter(lambda x: x['title'] not in old_job_titles, offers))
        # exclude boring tech
        boring_tech = ['php', '.net', 'angular', 'java', 'ruby on rails', 'wordpress']
        self.offers = list(filter(lambda x: x['technology'] not in boring_tech, self.offers))

    def prepare_email_content(self):
        mail = '<h2>No Fluff Jobs</h2>'
        for offer in self.offers:
            mail += f'''
            <a href='{offer['href']}'>
                {offer['title']} {offer['salary']}
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
