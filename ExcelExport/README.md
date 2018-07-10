## Overview
This example demonstrates the use of Topology endpoints and small amounts of code to create familiar documents, such as an Excel spreadsheet.  The intent in the example was to quickly build a list of possible firewall rules from Dynatrace detected process to process connections.

### From this:
![](./images/SmartScape.png)

### To this:
![](./images/Spreadsheet.png)

## Areas for follow-up
- Somehow show multiple IPs & ports better in the spreadsheet
- Incorporate Application & Service data as well
- Explore real-world possible uses

## Getting Started
This example app is very simple and does not have much logic built in.  On most OSes you'll already have python, but here are more detailed steps in case you're missing dependencies:
### Most Linux varients (assuming yum packages, sub in your package manager where necessary)
- Run: which python >/dev/null || sudo yum -y install python
- Run: which pip >/dev/null || sudo yum -y install python2-pip
- Run: sudo pip install pycurl
- Run: sudo pip install certifi
- Run: sudo pip install openpyxl
- Edit: dt-excel.py, change variable in SETUP VARIABLES section
- Run: python dt-excel.py

### MacOS (High Sierra)
- Run: /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
- Run: brew install openssl
- Run: brew install python
- Confirm: "which python3" gives /usr/local/bin/python3
- Run: sudo pip3 install --upgrade pip
- Run: pip3 install --user --install-option="--with-openssl" --install-option="--openssl-dir=/usr/local/opt/openssl" pycurl
- Run: pip3 install --user openpyxl
- Run: pip3 install --user certifi
- Edit: dt-excel.py, change variable in SETUP VARIABLES section
- Run: python3 dt-excel.py

### Windows
- Download latest: https://www.python.org/downloads/windows
- Install: be sure to pick options for "add to PATH" and "include PIP"
- Open command prompt
- Run: pip install pycurl
- Run: pip install certifi
- Run: pip install openpyxl
- Edit: dt-excel.py, change variable in SETUP VARIABLES section
- Run: python dt-excel.py

## Troubleshooting
- Status: 401
- - Your API token didn't work, please check the token and URL
- Status: 400
- - Your URL is incorrect
- Dependency or module not found errors
- - Your python install is incorrect or modules are missing, try the pip steps again and check for any errors there
