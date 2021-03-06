import subprocess

from pyscrape.loaders.loader import Loader


class BrewLoader(Loader):
    def __init__(self):
        self.updated_packages = []

    def scrape(self):
        self.update_packages()

    def prepare_email_content(self):
        return " ".join(self.updated_packages)

    def post_email(self):
        pass

    def update_packages(self):
        shell_command = ["brew", "upgrade"]
        sub = subprocess.Popen(
            shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = sub.communicate()
        output_string = output.decode("utf-8")
        packages = list(
            map(
                lambda line: line[14:],
                filter(lambda line: line.startswith("==> Upgrading "),
                       output_string.split("\n"))
            )
        )
        self.updated_packages = packages
