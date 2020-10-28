import sys
import argparse
import subprocess
import os
import glob
import shlex
import re
from pycompress.processors import jpeg, png
from pycompress.format import format_bytes


def init():
    parser = argparse.ArgumentParser("Images compressor")
    parser.add_argument("directory", type=str, nargs="?", default=os.getcwd(),
                        help="Directory to compress files in")
    parser.add_argument("-r", "-R", "--recursive", action="store_true",
                        help="Compress files reccursively")
    parser.add_argument("-qj", "--quality-jpeg", type=int, default=80,
                        help="Quality of compressed JPEG images (0-100)")
    parser.add_argument("-qp", "--quality-png", type=int, default=3,
                        help="Quality of compressed PNG images (0-7)")
    args = parser.parse_args()

    def get_images(extensions):
        images = []
        for extension in extensions:
            if args.recursive == True:
                images += glob.glob(
                    f"{args.directory}/**/*.{extension}", recursive=True)
            else:
                images += glob.glob(f"{args.directory}/*.{extension}")
        return images

    jpeg_images = get_images(["jpg", "jpeg", "JPG", "JPEG"])
    png_images = get_images(
        ["png", "PNG", "bmp", "BMP", "gif", "GIF", "pnm", "PNM", "tiff", "TIFF"])

    print(f"Found {len(jpeg_images) + len(png_images)} images")

    jpeg_data_saved = jpeg.compress(jpeg_images, args)
    png_data_saved = png.compress(png_images, args)
    total_data_saved = jpeg_data_saved + png_data_saved
    print(
        f"Finished compressing {len(jpeg_images) + len(png_images)}, total data saved {format_bytes(total_data_saved )}")
