#!/usr/bin/env python3
import sys
import argparse
import subprocess
import os
import glob
import shlex
import re

parser = argparse.ArgumentParser("Images compressor")
parser.add_argument("directory", type=str, nargs="?", default=os.getcwd(),
                    help="Directory to compress files in")
parser.add_argument("-r", "-R", "--recursive", action="store_true",
                    help="Compress files reccursively")
parser.add_argument("-q", "--quality", type=int, default=80,
                    help="Quality of compressed images")
args = parser.parse_args()


def getImages():
    extensions = ["jpg", "jpeg", "JPG", "JPEG"]
    images = []
    for extension in extensions:
        if args.recursive == True:
            images += glob.glob(
                f"{args.directory}/**/*.{extension}", recursive=True)
        else:
            images += glob.glob(f"{args.directory}/*.{extension}")
    return images


def format_bytes(size):
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'k', 2: 'M'}
    while size > power:
        size /= power
        n += 1
    return f"{int(size)} {power_labels[n]}b"


images = getImages()

print(f"Found {len(images)} images")
current_image_index = 1

total_data_saved = 0

for image in images:
    dirpath = os.path.realpath(args.directory)
    subdirpath = os.path.dirname(os.path.realpath(
        image).replace(f"{dirpath}/", "", 1))
    filename = os.path.basename(image)
    os.makedirs(f"{dirpath}/compressed/{subdirpath}", exist_ok=True)
    shellcommand = ["jpegoptim", f"-m{args.quality}", "-d",
                    f"{dirpath}/compressed/{subdirpath}", "-p", image]
    print(f"Compressing {current_image_index}/{len(images)} - {filename}")
    sub = subprocess.Popen(
        shellcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = sub.communicate()

    if error:
        error_string = error.decode("utf-8")
        print(error_string)
        print(shellcommand)
        if error_string.find("skipping"):
            print(
                f"Skipped {current_image_index}/{len(images)} - {filename}")
        else:
            print(error_string)
    else:
        output_string = output.decode("utf-8")
        pattern_percentage = re.compile(r"\(-?(\d|\.)*%\)")
        percentage = pattern_percentage.search(output_string)

        pattern_data_saved = re.compile(r"(\d*) --> (\d*)")
        data = pattern_data_saved.search(output_string)
        data_initial, data_end = data.groups()
        data_saved = int(data_initial) - int(data_end)

        total_data_saved += data_saved

        print(
            f"Compressed {current_image_index}/{len(images)} - {filename} - {percentage.group()} {format_bytes(data_saved)}")
    current_image_index += 1

print(
    f"Finished compressing {len(images)} images, total data saved {format_bytes(total_data_saved)}")
