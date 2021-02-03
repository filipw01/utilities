import re
import os
import subprocess
from pycompress.format import format_bytes


def get_bytes_saved(output: str):
    pattern_data_saved = re.compile(r"(\d*) --> (\d*)")
    data = pattern_data_saved.search(output)
    data_initial, data_end = data.groups()
    data_saved = int(data_initial) - int(data_end)
    return data_saved


def get_percentage_saved(output: str):
    pattern_percentage = re.compile(r"(-?(\d|\.)*%)")
    percentage = pattern_percentage.search(output)
    return percentage.group()


def compress(images, args):
    total_data_saved = 0

    for index, image in enumerate(images):
        dirpath = os.path.realpath(args.directory)
        subdirpath = os.path.dirname(os.path.realpath(
            image).replace(f"{dirpath}/", "", 1))
        filename = os.path.basename(image)
        os.makedirs(f"{dirpath}/compressed/{subdirpath}", exist_ok=True)
        shell_command = ["jpegoptim", f"-m{args.quality_jpeg}", "-d",
                        f"{dirpath}/compressed/{subdirpath}", "-p", image]
        print(f"Compressing {index+1}/{len(images)} - {filename}")
        sub = subprocess.Popen(
            shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = sub.communicate()

        if error:
            error_string = error.decode("utf-8")
            print(error_string)
            print(shell_command)
            if error_string.find("skipping") != -1:
                print(
                    f"Skipped {index+1}/{len(images)} - {filename}")
            else:
                print(error_string)
        else:
            out_string = output.decode("utf-8")
            percentage = get_percentage_saved(out_string)
            bytes_saved = get_bytes_saved(out_string)
            total_data_saved += bytes_saved

            print(
                f"Compressed {index+1}/{len(images)} - {filename} ({percentage} | {format_bytes(bytes_saved)})")

    print(
        f"Finished compressing {len(images)} JPEGish images, total data saved {format_bytes(total_data_saved)}")

    return total_data_saved
