from dotenv import load_dotenv
from pyscrape.html_email import send_html_email, build_html_email
from pyscrape.loaders.bankier.bankier import BankierLoader
from pyscrape.loaders.brew.brew import BrewLoader
from pyscrape.loaders.indeed.indeed import IndeedLoader
from pyscrape.loaders.just_join_it.just_join_it import JustJoinItLoader
from pyscrape.loaders.no_fluff_jobs.no_fluff_jobs import NoFluffJobsLoader


def init():
    load_dotenv(verbose=True)
    loaders = [
        BankierLoader(),
        BrewLoader(),
        JustJoinItLoader(),
        NoFluffJobsLoader(),
        IndeedLoader()
    ]
    for loader in loaders:
        loader.scrape()

    email = build_html_email(list(map(lambda x: x.prepare_email_content(), loaders)))
    send_html_email(email)

    for loader in loaders:
        loader.post_email()
