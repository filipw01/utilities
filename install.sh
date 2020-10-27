#!/bin/bash

# Install venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

DIR=$(cd "$(dirname "$0")" && pwd)

# Create executables

mkdir "${DIR}/bin"

## compress.py
echo "#!${DIR}/venv/bin/python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pycompress.compress import init

init()" >${DIR}/bin/compress.py

## scrape.py
echo "#!${DIR}/venv/bin/python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pyscrape.scrape import init

init()" >${DIR}/bin/scrape.py

# Add execute permissions
chmod +x ${DIR}/bin/*

#Create launchd file
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
    <dict>
        <key>Label</key>
        <string>org.filip.scrape</string>
        <key>ProgramArguments</key>
        <array>
            <string>${DIR}/bin/scrape.py</string>
        </array>
        <key>StartCalendarInterval</key>
        <array>
            <dict>
                <key>Hour</key>
                <integer>6</integer>
                <key>Minute</key>
                <integer>0</integer>
            </dict>
            <dict>
                <key>Hour</key>
                <integer>16</integer>
                <key>Minute</key>
                <integer>0</integer>
            </dict>
            <dict>
                <key>Hour</key>
                <integer>22</integer>
                <key>Minute</key>
                <integer>0</integer>
            </dict>
        </array>
    </dict>
</plist>" >${DIR}/pyscrape/pyscrape.plist

# Add bin directory to $PATH if not added
# TODO:

# Ask for password and email
echo "What's your email username (email)?"
read EMAIL
echo "What's your email password?"
read PASSWORD

echo "EMAIL_USERNAME=${EMAIL}
EMAIL_PASSWORD=${PASSWORD}" >${DIR}/pyscrape/.env

# Add MacOS cron job using launchd
cp ./pyscrape/pyscrape.plist ~/Library/LaunchAgents/pyscrape.plist
launchctl load ~/Library/LaunchAgents/pyscrape.plist
