import re
from dotenv import load_dotenv
from pyscrape.loaders.bankier.bankier import BankierLoader
from pyscrape.html_email import send_html_email, build_html_email
from pyscrape.loaders.brew.brew import BrewLoader


def init():

    load_dotenv(verbose=True)

    bankier = BankierLoader()
    bankier_articles = bankier.get_articles()

    brew = BrewLoader()
    brew.update_packages()

    email = build_html_email(articles=bankier_articles, updated_packages=brew.updated_packages)

    send_html_email(email)
    bankier.save_scraped_articles()
    bankier.remove_old_articles()
