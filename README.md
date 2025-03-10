# Energibridge Analytics

## Overview
This project sets up a PostgreSQL database and Grafana for analytics purposes using Docker Compose.

## Prerequisites
- Docker
- Docker Compose

## Setup

1. Clone the repository:
    ```sh
    git clone git@github.com:krisvanmelis/energibridge-analytics.git
    cd energibridge-analytics
    ```

2. Start the services:
    ```sh
    docker-compose up -d
    ```

3. Access Grafana:
    Open your browser and go to `http://localhost:3000`. Use the following credentials to log in:
    - Username: `admin`
    - Password: `admin`

4. Access PostgreSQL:
    The PostgreSQL database is accessible on port `5432`. Use the following credentials:
    - Username: `admin`
    - Password: `admin`
    - Database: `analytics`

## Provisioning
Grafana is pre-configured with a PostgreSQL datasource and a default dashboard called "Energibridge Dashboard". The provisioning files are located in the `grafana/provisioning` directory. The dashboard JSON file is located in the `grafana/dashboards` directory.

## Stopping the services
To stop the services, run:
```sh
docker-compose down
```

## Cleaning up
To remove all data, run:
```sh
docker-compose down -v
```
