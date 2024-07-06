#!/bin/bash

#cd addon
#sudo docker compose down
#sudo docker compose pull
#sudo docker compose up -d
#clear
#IP=$(curl -4 -s ifconfig.me)
#echo "Update completed!"
#echo "Your addon is accessible at https://$domainName/"


curl -o main.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/main.py
cd utils
curl -o get_content.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/utils/get_content.py
curl -o get_cached.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/utils/get_cached.py
curl -o filter_results.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/utils/filter_results.py
curl -o process_results.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/utils/process_results.py
curl -o get_availability.py https://raw.githubusercontent.com/Willou-Gillou/stremio-jackett/main/3.0.14-indus/utils/get_availability.py
cd ..
echo "Update completed!"
