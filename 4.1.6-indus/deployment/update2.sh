#!/bin/bash

curl -o main.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/4.1.6-indus/source/main.py
cd jackett
curl -o jackett_service.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/4.1.6-indus/source/jackett/jackett_service.py
cd ..
cd utils
curl -o filter_results.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/4.1.6-indus/source/utils/filter_results.py
cd ..

echo "Update completed!"