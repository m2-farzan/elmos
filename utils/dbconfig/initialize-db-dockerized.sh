#!/bin/bash

sudo docker build -t elmos-initialize-db $ELMOS/utils/dbconfig/
sudo docker create --name ${PROJECT_BASENAME}-1 --network container:${PROJECT_BASENAME}-db -e "DB_USER=$DB_USER" -e "DB_PASS=$DB_PASS" -e "DB_DATABASE=$DB_DATABASE" elmos-initialize-db
sudo docker cp groups.json ${PROJECT_BASENAME}-1:/
sudo docker cp comgps.json ${PROJECT_BASENAME}-1:/
sudo docker start --interactive ${PROJECT_BASENAME}-1
sudo docker rm ${PROJECT_BASENAME}-1
