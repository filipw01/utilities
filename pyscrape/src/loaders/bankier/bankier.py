import time
import boto3
from bs4 import BeautifulSoup
import requests
import re

from ..loader import Loader

client = boto3.client('dynamodb', region_name='eu-central-1')


class BankierLoader(Loader):
    def __init__(self):
        self.new_scraped_articles = []
        self.scraped_titles = []
        self.articles = []

    def scrape(self):
        req = requests.get('https://bankier.pl')

        soup = BeautifulSoup(req.text, features='html.parser')
        main = soup.find(class_='l-main')
        links = main.find_all(
            'a', attrs={'data-vr-contentbox': re.compile(r'news')})

        total = len(links)
        self.articles = []
        self.new_scraped_articles = []
        self.scraped_titles = []
        old_articles = []
        no_image_articles = []
        no_title_articles = []
        boring_articles = []
        for link in links:
            img = link.find('img')
            article_link = self.absolute_link(link['href'])
            title_node = link.find(
                class_='m-title-with-label-item__title')
            if title_node is None:
                no_title_articles.append(link)
                continue
            if img is None:
                no_image_articles.append(link)
                continue
            title = title_node.text.strip()
            if self.is_past_article(title):
                old_articles.append(link)
                continue

            if self.is_boring(title):
                boring_articles.append(link)
                continue
            try:
                req = requests.get(article_link)
                soup = BeautifulSoup(req.text, features='html.parser')
                article = soup.find('article')
                lead_node = article.find(
                    class_='lead') or article.find('b')
                lead = lead_node.text
            except:
                lead = 'Nie udało się pobrać treści'

            current_epoch = int(time.time())
            seconds_in_2_days = 60 * 60 * 48
            self.new_scraped_articles.append(
                {'url': article_link, 'name': title, 'ttl': current_epoch + seconds_in_2_days}
            )
            self.articles.append((article_link, img['src'], title, lead))
            print(f'Bankier: Scraped {len(self.articles)} - {title}')

        print(f'Bankier: Scraped in total {len(self.articles)}/{total}')
        omitted_articles_count = len(old_articles) + len(no_title_articles) + len(no_image_articles) + len(
            boring_articles)
        if omitted_articles_count > 0:
            print(f'{"":9}Omitted {omitted_articles_count} articles:')
            if len(old_articles) > 0:
                print(f'{"":17}{len(old_articles)} old')
            if len(boring_articles) > 0:
                print(f'{"":17}{len(boring_articles)} boring')
            if len(no_image_articles) + len(no_title_articles) > 0:
                print(f'{"":17}{len(no_image_articles) + len(no_title_articles)} invalid')

    def prepare_email_content(self):
        body = ''
        for link, img_src, title, lead in self.articles:
            body += f'''
                    <a href='{link}'>
                        <img src='{img_src}'/>
                        <h1>{title}</h1>
                        <p>{lead}</p>
                    </a>
                    '''
        return body

    def post_email(self):
        self.save_scraped_articles()

    @staticmethod
    def is_boring(title):
        boring_fragments = [
            'zapowiedź dnia',
            'to był dzień',
            'pekao',
            'budowlan',
            'witucki',
            'kuczyński',
            'bankier.pl',
            'najważniejsze wiadomości',
            'przerw',
            'nieruchomo',
            'lidl',
            'biedronka',
            'huuuge',
            'loka',
            'gpw',
            'kredy',
            'frank',
            'kulczyk',
            'PKO',
            'paliw',
            'kurs',
            'giełd',
            'czyta',
            'korekta'
        ]
        for boring in boring_fragments:
            if boring in title.lower():
                return True
        return False

    @staticmethod
    def is_past_article(title):
        result = client.get_item(TableName="bankierTable", Key={
            'name': {
                'S': title
            }
        })
        if 'Item' in result:
            return True
        return False

    def save_scraped_articles(self):
        def request_from_article(article):
            return {
                'PutRequest': {
                    'Item': {
                        'name': {'S': article['name']},
                        'url': {'S': article['url']},
                        'ttl': {'N': str(article['ttl'])}
                    }
                }
            }

        def chunks(whole, chunk_size):
            for i in range(0, len(whole), chunk_size):
                yield whole[i:i + chunk_size]

        put_requests = [request_from_article(article) for article in self.new_scraped_articles]
        for requests_chunk in chunks(put_requests, 25):
            client.batch_write_item(
                RequestItems={
                    'bankierTable': requests_chunk
                }
            )

    @staticmethod
    def absolute_link(link: str):
        if link.startswith('/'):
            return f'https://bankier.pl{link}'
        return link
