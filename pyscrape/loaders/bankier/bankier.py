from bs4 import BeautifulSoup
import requests
import os
import re


class BankierLoader:

    def __init__(self):
        self.scraped_titles = []
        self.bankier_loader_dir = os.path.dirname(os.path.realpath(__file__))

    def get_articles(self):
        req = requests.get('https://bankier.pl')

        soup = BeautifulSoup(req.text, features="html.parser")
        main = soup.find(class_="l-main")
        links = main.find_all(
            "a", attrs={"data-vr-contentbox": re.compile(r"news")})

        total = len(links)
        articles = []

        for link in links:
            img = link.find("img")
            article_link = self.absoluteLink(link["href"])
            title_node = link.find(
                class_="m-title-with-label-item__title")
            if title_node is None:
                print(f"Bankier: Skipped: no title")
                continue
            if img is None:
                print(f"Bankier: Skipped: no image")
                continue
            title = title_node.text.strip()
            if title in self.get_past_articles_titles():
                print(f"Bankier: Skipped: already scraped")
                continue

            if self.is_boring(title):
                print(f"Bankier: Boring")
                continue
            try:
                req = requests.get(article_link)
                soup = BeautifulSoup(req.text, features="html.parser")
                article = soup.find("article")
                lead_node = article.find(
                    class_="lead") or article.find("b")
                lead = lead_node.text
            except:
                lead = "Nie udało się pobrać treści"

            self.scraped_titles.append(title)
            articles.append((article_link, img["src"], title, lead))
            print(f"Bankier: Scraped {len(articles)} - {title}")

        print(f"Bankier: Scraped in total {len(articles)}/{total}")

        return articles

    def is_boring(self, title):
        boring_fragments = [
            "Zapowiedź dnia",
            "To był dzień",
            "Pekao",
            "budowlan",
            "Witucki",
            "Kuczyński",
            "Bankier.pl",
            "bankier.pl",
            "Najważniejsze wiadomości",
        ]
        for boring in boring_fragments:
            if boring in title:
                return True
        return False

    def get_past_articles_titles(self):
        with open(f"{self.bankier_loader_dir}/pastArticles.txt", "r") as file:
            return file.read().split("\n")[:-1]

    def save_scraped_articles(self):
        with open(f"{self.bankier_loader_dir}/pastArticles.txt", "a") as file:
            file.writelines("\n".join(self.scraped_titles) + "\n")

    def remove_old_articles(self):
        with open(f"{self.bankier_loader_dir}/pastArticles.txt", "r+") as file:
            articles = file.read().split("\n")[:-1]
            last_100_article_links = "\n".join(articles[-100:])
            file.seek(0)
            file.truncate()
            file.write(last_100_article_links + "\n")

    def absoluteLink(self, link: str):
        if link.startswith("/"):
            return f"https://bankier.pl{link}"
        return link
