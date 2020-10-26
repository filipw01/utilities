#!/bin/bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Create executables
// TODO

#Create launchd file
// TODO

#Ask for password and email
// TODO

# Add MacOS cron job using launchd
cp ./pyscrape/pyscrape.plist ~/Library/LaunchAgents/pyscrape.plist
launchctl load ~/Library/LaunchAgents/pyscrape.plist
