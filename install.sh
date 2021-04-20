#!/bin/bash

DIR=$(cd "$(dirname "$0")" && pwd)

# Install venv
python3 -m venv venv
${DIR}/venv/bin/pip install --upgrade pip
${DIR}/venv/bin/pip install -r requirements.txt

# Create executables

mkdir "${DIR}/bin"

## compress.py
echo "#!${DIR}/venv/bin/python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pycompress.compress import init

init()" >${DIR}/bin/compress.py

# Add execute permissions
chmod +x ${DIR}/bin/*
