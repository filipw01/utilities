from dotenv import load_dotenv
from pyscrape.loaders.bankier.bankier import BankierLoader
from pyscrape.html_email import send_html_email, build_html_email
from pyscrape.loaders.brew.brew import BrewLoader


def init():
    load_dotenv(verbose=True)
    loaders = [
        BankierLoader(),
        BrewLoader()
    ]
    for loader in loaders:
        loader.scrape()

    email = build_html_email(list(map(lambda x: x.prepare_email_content(), loaders)))
    send_html_email(email)

    for loader in loaders:
        loader.post_email()
