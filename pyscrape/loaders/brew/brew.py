import subprocess


class BrewLoader:

    def __init__(self):
        self.updated_packages = []

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
