#!/bin/bash

git pull origin master

export $(xargs <.env)

# UPDATE GREEN

docker-compose -f docker-compose-green.yml up --build -d

sleep 5 # Let the new service wake up

cp /etc/nginx/sites-available/ir.elmos-vahed /etc/nginx/sites-available/ir.elmos-vahed.backup-blue
sed -i "s/$UI_PORT/$UI_PORT_GREEN/g" /etc/nginx/sites-available/ir.elmos-vahed

nginx -t

if [[ $? -ne 0 ]]; then
    echo "Error: nginx config got nuked. Running back to backup."
    mv /etc/nginx/sites-available/ir.elmos-vahed.backup-blue /etc/nginx/sites-available/ir.elmos-vahed
    exit 1
fi

nginx -s reload

# UPDATE BLUE

docker-compose up -d --no-deps --build elmos

sleep 5 # Let the new service wake up

cp /etc/nginx/sites-available/ir.elmos-vahed /etc/nginx/sites-available/ir.elmos-vahed.backup-green
sed -i "s/$UI_PORT_GREEN/$UI_PORT/g" /etc/nginx/sites-available/ir.elmos-vahed

nginx -t

if [[ $? -ne 0 ]]; then
    echo "Error: nginx config got nuked. Running back to backup."
    cp /etc/nginx/sites-available/ir.elmos-vahed /etc/nginx/sites-available/ir.elmos-vahed.backup-green
    exit 1
fi

nginx -s reload

docker-compose -f docker-compose-green.yml stop
