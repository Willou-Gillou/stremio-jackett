#!/bin/bash

curl -o main.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/4.1.6-indus/source/main.py
cd jackett

curl -o jackett_service.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/4.1.6-indus/source/jackett/jackett_service.py

echo "Update completed!"