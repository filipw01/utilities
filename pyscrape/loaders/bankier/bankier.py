from bs4 import BeautifulSoup
import requests
import os
import re


class BankierLoader:

    def __init__(self):
        self.scraped_links = []
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
            if img and article_link not in self.get_past_articles_links():
                title = link.find(
                    class_="m-title-with-label-item__title").text

                try:
                    req = requests.get(article_link)
                    soup = BeautifulSoup(req.text, features="html.parser")
                    article = soup.find("article")
                    lead_node = article.find(
                        class_="lead") or article.find("b")
                    lead = lead_node.text
                except:
                    lead = "Nie udało się pobrać treści"

                self.scraped_links.append(article_link)
                articles.append((article_link, img["src"], title, lead))
                print(f"Bankier: Scraped {len(articles)}")

            else:
                print(f"Bankier: Skipped")

        print(f"Bankier: Scraped in total {len(articles)}/{total}")

        return articles

    def get_past_articles_links(self):
        with open(f"{self.bankier_loader_dir}/pastArticles.txt", "r") as file:
            return file.read().split("\n")

    def save_scraped_articles(self):
        with open(f"{self.bankier_loader_dir}/pastArticles.txt", "a") as file:
            file.writelines("\n".join(self.scraped_links) + "\n")

    def absoluteLink(self, link: str):
        if link.startswith("/"):
            return f"https://bankier.pl{link}"
        return link
