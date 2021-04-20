from abc import abstractmethod

from .loader import Loader


class JobLoader(Loader):
    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def prepare_email_content(self):
        pass

    def __init__(self):
        self.loader_dir = None
        self.offers = []

    def save_scraped_jobs(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'a') as file:
            file.writelines('\n'.join(map(lambda x: x['title'], self.offers)) + '\n')

    def remove_old_jobs(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'r+') as file:
            jobs = file.read().split('\n')[:-1]
            last_500_jobs = '\n'.join(jobs[-500:])
            file.seek(0)
            file.truncate()
            file.write(last_500_jobs + '\n')

    def get_past_job_titles(self):
        with open(f'{self.loader_dir}/pastJobs.txt', 'r') as file:
            return file.read().split('\n')[:-1]

    def post_email(self):
        self.save_scraped_jobs()
        self.remove_old_jobs()
