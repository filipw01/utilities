import os
import requests

from pyscrape.loaders.job_loader import JobLoader


class JustJoinItLoader(JobLoader):
    def __init__(self):
        super().__init__()
        self.offers = []
        self.loader_dir = os.path.dirname(os.path.realpath(__file__))

    def scrape(self):
        req = requests.get('https://justjoin.it/api/offers')
        r = req.json()
        self.offers = r
        # offer structure
        #
        # title,
        # street,
        # city,
        # country_code,
        # address_text,
        # marker_icon,
        # workplace_type,
        # company_name,
        # company_url,
        # company_size,
        # experience_level,
        # latitude
        # longitude
        # published_at
        # remote_interview
        # id
        # employment_types: Array<{type,salary:{from,to,currency}}>
        # company_logo_url
        # skills: Array<{name,level}
        # remote
        all_offers_count = len(self.offers)
        for offer in self.offers:
            offer['title'] += f' at {offer["company_name"]} in {offer["city"]}'
        self.offers, old, boring, non_remote = self.filter_jobs()
        print(f'JustJoinIt: Scraped {len(self.offers)}/{all_offers_count}')
        print(f'{"":13}Omitted {len(old) + len(boring) + len(non_remote)} jobs:')
        print(f'{"":20}{len(old)} old')
        print(f'{"":20}{len(boring)} boring')
        print(f'{"":20}{len(non_remote)} non-remote')

    def filter_jobs(self):
        result = []
        old = []
        boring = []
        non_remote = []
        old_job_titles = self.get_past_job_titles()
        boring_tech = {'php', '.net', 'angular', 'java', 'ruby', 'wordpress', 'xamarin', 'c++', 'java',
                       'elixir', '.net core', 'c#', 'go'}

        for job in self.offers:
            regular_level_tech = {skill['name'].lower() for skill in job['skills'] if skill['level'] >= 3}
            if job['title'] in old_job_titles:
                old.append(job)
            elif not job['remote']:
                non_remote.append(job)
            elif len(regular_level_tech & boring_tech) > 0 \
                    or job['experience_level'] == 'senior' \
                    or 'javascript' not in regular_level_tech:
                boring.append(job)
            else:
                result.append(job)

        return result, old, boring, non_remote

    def prepare_email_content(self):
        mail = '<h2>JustJoinIt</h2>'
        for offer in self.offers:
            salary = [
                f'{employment["type"]}: {employment["salary"]["from"]} - {employment["salary"]["to"]}{employment["salary"]["currency"]}'
                for employment in offer['employment_types'] if employment["salary"] is not None]
            mail += f'''
            <a style="display: flex; align-items: center;" href='{JustJoinItLoader.absolute_link(offer['id'])}'>
                <img style="max-width: 50px; max-height: 50px; margin-right: 20px;" src="{offer['company_logo_url']}"/>
                {offer['title']} {'<br>'.join(salary)}
            </a>
            '''
        return mail

    @staticmethod
    def absolute_link(offer_id: str):
        return f'https://justjoin.it/offers/{offer_id}'
