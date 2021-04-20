from src.html_email import send_html_email, build_html_email
from src.loaders.bankier.bankier import BankierLoader


def init(event=None, context=None):
    loaders = [
        BankierLoader(),
    ]
    for loader in loaders:
        loader.scrape()

    email = build_html_email(list(map(lambda x: x.prepare_email_content(), loaders)))
    send_html_email(email)

    for loader in loaders:
        loader.post_email()
