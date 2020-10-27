from bs4 import BeautifulSoup
import requests
import re
import smtplib
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date


def init():
    pyscrape_dir = os.path.dirname(os.path.realpath(__file__))

    load_dotenv(
        verbose=True)

    req = requests.get('https://bankier.pl')

    soup = BeautifulSoup(req.text, features="html.parser")
    main = soup.find(class_="l-main")
    links = main.find_all(
        "a", attrs={"data-vr-contentbox": re.compile(r"news")})

    total = len(links)

    body = ""

    def absoluteLink(link: str):
        if link.startswith("/"):
            return f"https://bankier.pl{link}"
        return link

    skipped = 0
    scraped_links = []
    past_articles = []
    email = ""

    with open(f"{pyscrape_dir}/pastArticles.txt", "r") as file:
        past_articles = file.read().split("\n")

    for index, link in enumerate(links):
        img = link.find("img")
        img_html = ""
        article_link = absoluteLink(link["href"])
        if img and article_link not in past_articles:
            article_title = link.find(
                class_="m-title-with-label-item__title").text
            lead = ""
            try:
                req = requests.get(article_link)
                soup = BeautifulSoup(req.text, features="html.parser")
                article = soup.find("article")
                lead_node = article.find(class_="lead") or article.find("b")
                lead = lead_node.text
            except():
                lead = "Nie udało się pobrać treści"

            img_html = f"""<img src="{absoluteLink(img["src"])}"/> """
            body += f"""
            <a href="{article_link}">
                {img_html}
                <h1>{article_title}</h1>
                <p>{lead}</p>
            </a>
            """
            scraped_links.append(article_link)
            print(f"Scraped {index+1}/{total}")
            email = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email</title>
        <style>
            table {{
                margin: auto;
            }}
            a {{
                display: block;
                margin: 2rem 0;
                font-family: system-ui;
                text-decoration: none;
                color: black;
            }}
            img{{
                display: block;
                width: 100%;
            }}
            h1{{
                font-size: 1.5rem;
            }}
            h1, p{{
                display: block;
                margin: 1rem 0;
            }}
        </style>
    </head>
    <body>
        <table border="0" cellpadding="0" cellspacing="0" width="600">
        <tr>
            <td align="center" valign="top">
                {body}
            </td>
        </tr>
    </body>
    </html>
    """
        else:
            skipped += 1
            print(f"Skipped {index+1}/{total}")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(os.getenv("EMAIL_USERNAME"), os.getenv("EMAIL_PASSWORD"))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Bankier - {date.today()}"
    msg["From"] = "news@bankier.pl"
    msg["To"] = "wachowiakf@gmail.com"

    part1 = MIMEText("News from bankier.pl", "plain")
    part2 = MIMEText(email, "html")

    msg.attach(part1)
    msg.attach(part2)

    server.sendmail("news@bankier.pl", "wachowiakf@gmail.com", msg.as_string())
    server.quit()

    with open(f"{pyscrape_dir}/pastArticles.txt", "a") as file:
        file.writelines("\n".join(scraped_links) + "\n")

    print(f"Skipped {skipped}")
    print(f"Scraped {total-skipped}")
