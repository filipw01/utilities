from src.vaccine_check import VaccineChecker


def init(event=None, context=None):
    check = VaccineChecker()
    check.scrape()
