#!/bin/bash
docker-compose down

#Clean leger (on garde le cache)
docker network prune -f
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
rm -rf ./airflow/logs
rm -rf ./airflow/plugins

mkdir ./airflow/logs ./airflow/plugins
source ./.env
sudo chown -R $USER $AIRFLOW_PGDATA


# Create the "outside" network
docker network create outside

#sudo docker-compose build --no-cache
docker-compose build
docker-compose up