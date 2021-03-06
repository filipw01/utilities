import requests
from bs4 import BeautifulSoup

from pyscrape.loaders.loader import Loader


class JustJoinItLoader(Loader):
    def __init__(self):
        pass

    def scrape(self):
        req = requests.get('https://justjoin.it/remote-global/javascript')

        soup = BeautifulSoup(req.text, features="html.parser")

        root = soup.find(id="root")
        children = root.children
        print(children)

    def prepare_email_content(self):
        return ""

    def post_email(self):
        pass
