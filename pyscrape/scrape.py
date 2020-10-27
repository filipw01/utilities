import re
from dotenv import load_dotenv
from pyscrape.loaders.bankier.bankier import BankierLoader
from pyscrape.html_email import send_html_email, build_html_email


def init():

    load_dotenv(verbose=True)

    bankier = BankierLoader()

    bankier_articles = bankier.get_articles()

    email = build_html_email(bankier_articles)

    send_html_email(email)
    bankier.save_scraped_articles()
