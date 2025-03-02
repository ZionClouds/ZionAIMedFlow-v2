#!/usr/bin/env bash
cat >/etc/motd <<EOL
  _____
  /  _  \ __________ _________   ____
 /  /_\  \\___   /  |  \_  __ \_/ __ \
/    |    \/    /|  |  /|  | \/\  ___/
\____|__  /_____ \____/ |__|    \___  >
        \/      \/                  \/
A P P   S E R V I C E   O N   L I N U X

Documentation: http://aka.ms/webapp-linux
NodeJS quickstart: https://aka.ms/node-qs

EOL
cat /etc/motd

service ssh start
#service nscd start

# Get environment variables to show up in SSH session
eval $(printenv | awk -F= '{print "export " $1"="$2 }' >> /etc/profile)

sed -i -e "s|/api/|$backendUri|g" /usr/src/app/server/public/index.html

# if [[ -z "${AppDebug}" ]]; then
#   debugreplace="false"
# else
#   debugreplace="${AppDebug}"
# fi
# sed -i -e "s|###false###|$debugreplace|g" /usr/src/app/server/public/index.html

cd /usr/src/app/server
pm2 start server.js --no-daemon