from dotenv import load_dotenv
from vaccine_check.vaccine_check import VaccineChecker


def init(event=None, context=None):
    load_dotenv(verbose=True)
    check = VaccineChecker()
    check.scrape()
