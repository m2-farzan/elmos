#!/bin/bash

sudo docker build -t elmos-initialize-db $ELMOS/utils/dbconfig/
sudo docker create --name elmos-initialize-db-1 --network container:elmos-db -e "DB_USER=$DB_USER" -e "DB_PASS=$DB_PASS" -e "DB_DATABASE=$DB_DATABASE" elmos-initialize-db
sudo docker cp groups.json elmos-initialize-db-1:/
sudo docker cp comgps.json elmos-initialize-db-1:/
sudo docker start --interactive elmos-initialize-db-1
sudo docker rm elmos-initialize-db-1
