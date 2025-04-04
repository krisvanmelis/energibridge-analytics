# Energibridge Analytics

## Overview
Energibridge Analytics is a tool for analyzing and visualizing energy-related performance measurements from computer systems. It provides a comprehensive pipeline for data processing, analysis, and visualization using a Flask web application and Grafana dashboards.

## Features
- Data collection and preprocessing of energy and performance metrics
- Statistical analysis of measurements across different experiment groups
- Interactive visualizations with customizable dashboards
- Support for various measurement types (CPU power, core frequency, memory usage, etc.)
- Different experiment types (time series plots, statistical comparisons, significance tests)

## Prerequisites
- Docker and Docker Compose
- Basic understanding of energy/power measurements

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone git@github.com:krisvanmelis/energibridge-analytics.git
   cd energibridge-analytics
   ```

2. **Start the services:**
   ```sh
   docker-compose up --build
   ```
   This will start all necessary services: the Flask web app, PostgreSQL database, Grafana, and Nginx for hosting CSV files.

3. **Access the web interface:**
   Open your browser and navigate to [http://localhost:5000/](http://localhost:5000/)

4. **Create experiment groups:**
   - Place your CSV measurement data in the `csv-data/input/[folder-name]` directory
   - In the web interface, add a new group with a name and select the appropriate folder

5. **Configure experiments:**
   - Create a new experiment by selecting groups to include
   - Choose an experiment type (Plot over time, Compare 2 groups, Overall statistics)
   - Select measurement types to analyze
   - Click "Add Experiment"

6. **Generate visualizations:**
   - Click "Generate Visualizations" to create Grafana dashboards
   - Follow the provided links to view your dashboards

7. **Access Grafana directly:**
   - Navigate to [http://localhost:3000/](http://localhost:3000/)
   - Login with default credentials: username `admin`, password `admin`

## Experiment Types

- **Plot over time**: Visualize measurements over time with statistical quartiles
- **Compare 2 groups**: Statistical comparison between two experiment groups with significance testing
- **Overall statistics**: General statistical analysis of measurements

## Project Structure and Code Organization

### Directory Structure
```
energibridge-analytics/
├── preprocessing/          # Flask application and data processing logic
│   ├── src/                # Source code for preprocessing and analysis
│   │   ├── models/         # Data models and type definitions
│   │   ├── templates/      # Flask HTML templates
│   │   └── static/         # CSS, JS, and other static assets
├── csv-data/               # Input and processed CSV files
│   ├── input/              # Raw measurement data
│   └── output/             # Processed data and analysis results
├── grafana/                # Grafana configuration
│   ├── dashboards/         # Generated dashboard JSON files
│   └── provisioning/       # Grafana provisioning config
├── nginx/                  # Nginx configuration for serving CSV files
└── images/                 # Generated charts and visualizations
```

### Key Components
- **Flask App (`preprocessing/src/app.py`)**: Core application handling web interface and API endpoints
- **Group Service**: Manages experiment groups and their associated data
- **Experiment Service**: Handles experiment configurations and analysis
- **Grafana Service**: Generates Grafana dashboard configurations
- **Measurement Types**: Defines supported metrics (power, energy, temperature, etc.)
- **Experiment Types**: Defines analysis and visualization approaches

### Development Workflow
1. Add new measurement data to `csv-data/input/[folder-name]`
2. Use the web interface to create experiment groups and configurations
3. Process data and generate visualizations
4. Access and customize the generated Grafana dashboards

### Extending the Project
- Add new measurement types in `models/types/measurement_type.py`
- Create new visualization templates in the Grafana service
- Implement additional statistical analysis in the experiment service

## Stopping the Services
To stop all services, run:
```sh
docker-compose down
```

## Cleaning up
To remove all data, run:
```sh
docker-compose down -v
```
