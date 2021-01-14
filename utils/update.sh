#!/bin/bash

git pull origin master

export $(xargs <.env)

# UPDATE GREEN

docker-compose -f docker-compose-green.yml up --build -d

sleep 5 # Let the new service wake up

cp ${NGINX_CONF_PATH} ${NGINX_CONF_PATH}.backup-blue
sed -i "s/$UI_PORT/$UI_PORT_GREEN/g" ${NGINX_CONF_PATH}

nginx -t

if [[ $? -ne 0 ]]; then
    echo "Error: nginx config got nuked. Running back to backup."
    mv ${NGINX_CONF_PATH}.backup-blue ${NGINX_CONF_PATH}
    exit 1
fi

nginx -s reload

# UPDATE BLUE

docker-compose up -d --no-deps --build elmos

sleep 5 # Let the new service wake up

cp ${NGINX_CONF_PATH} ${NGINX_CONF_PATH}.backup-green
sed -i "s/$UI_PORT_GREEN/$UI_PORT/g" ${NGINX_CONF_PATH}

nginx -t

if [[ $? -ne 0 ]]; then
    echo "Error: nginx config got nuked. Running back to backup."
    cp ${NGINX_CONF_PATH} ${NGINX_CONF_PATH}.backup-green
    exit 1
fi

nginx -s reload

docker-compose -f docker-compose-green.yml stop
