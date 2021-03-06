from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def prepare_email_content(self):
        pass

    @abstractmethod
    def post_email(self):
        pass
