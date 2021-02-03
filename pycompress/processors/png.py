import re
import os
import subprocess
from pycompress.format import format_bytes


def get_bytes_saved(output: str):
    pattern_data_saved = re.compile(
        r"file size = \d* bytes \((\d*) bytes", re.MULTILINE)
    data = pattern_data_saved.search(output)
    if(data == None):
        return 0
    return int(data.groups()[0])


def get_percentage_saved(output: str):
    pattern_percentage = re.compile(r"(-?(\d|\.)*%)", re.MULTILINE)
    percentage = pattern_percentage.search(output)
    if(percentage == None):
        return "0.00%"
    return percentage.group()


def compress(images, args):
    total_data_saved = 0

    for index, image in enumerate(images):
        dirpath = os.path.realpath(args.directory)
        subdirpath = os.path.dirname(os.path.realpath(
            image).replace(f"{dirpath}/", "", 1))
        filename = os.path.basename(image)
        os.makedirs(f"{dirpath}/compressed/{subdirpath}", exist_ok=True)
        shell_command = ["optipng", image, "-dir",
                        f"{dirpath}/compressed/{subdirpath}", f"-o{args.quality_png}"]
        print(f"Compressing {index+1}/{len(images)} - {filename}")
        sub = subprocess.Popen(
            shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = sub.communicate()

        out_string = error.decode("utf-8")
        percentage = get_percentage_saved(out_string)
        bytes_saved = get_bytes_saved(out_string)
        total_data_saved += bytes_saved

        print(
            f"Compressed {index+1}/{len(images)} - {filename} ({percentage} | {format_bytes(bytes_saved)})")

    print(
        f"Finished compressing {len(images)} PNGish images, total data saved {format_bytes(total_data_saved)}")

    return total_data_saved
