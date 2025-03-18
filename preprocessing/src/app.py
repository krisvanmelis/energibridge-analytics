"""
Module containing Flask application for generating grafana dashboard configurations.
"""
import json
import os

import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect, Response

from dashboards import generate_dashboard
from visualizations import VisualizationConfig, VisualizationType

app = Flask(__name__)

# Sample list to store configurations
configs = [
    VisualizationConfig("Power Analysis", VisualizationType.SYSTEM_ENERGY,
                        "csv-data/preprocessing_output/result_processed.csv"),
]
# Path where Grafana dashboard config will be saved
DASHBOARD_CONFIG_PATH = '../var/lib/grafana/dashboards/test_config.json'
GRAFANA_URL = 'http://localhost:3000'

OUTPUT_FOLDER = 'csv-data/preprocessing_output/'


@app.route('/')
def home() -> str:
    """
    Endpoint to render home page where visualizations can be configured.

    :return: Rendered home page
    """
    return render_template('index.html', configs=configs)


@app.route('/add_config', methods=['POST'])
def add_config() -> Response:
    """
    Endpoint to add new config to the dashboard.

    :return: JSON response with new configs list
    """
    data = request.form
    new_config = VisualizationConfig(data['name'], VisualizationType(int(data['type'])), data['csv_path'])
    configs.append(new_config)
    return jsonify({'status': 'success', 'configs': [c.to_dict() for c in configs]})


@app.route('/delete_config', methods=['POST'])
def delete_config() -> Response:
    """
    Endpoint to delete a config from the dashboard.

    :return: JSON response with new configs
    """
    config_name = request.form['name']
    global configs
    configs = [c for c in configs if c.name != config_name]
    return jsonify({'status': 'success', 'configs': [c.to_dict() for c in configs]})


@app.route('/generate_visualizations')
def generate_visualizations() -> Response:
    """
    Endpoint to generate visualizations (and grafana dashboard configuration).
    Also redirects to Grafana.

    :return: JSON response with redirect
    """
    # Generate and save json file which configures Grafana dashboard.
    grafana_config = generate_dashboard(configs)
    dir_name = os.path.dirname(DASHBOARD_CONFIG_PATH)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(DASHBOARD_CONFIG_PATH, 'w') as json_file:
        json.dump(grafana_config, json_file, indent=4)  # `indent=4` for pretty formatting

    return redirect(GRAFANA_URL)


@app.route('/get_configs', methods=['GET'])
def get_configs() -> Response:
    """
    Endpoint to get all configs from the dashboard.

    :return: JSON response with all configs
    """
    return jsonify([c.to_dict() for c in configs])


@app.route('/process', methods=['POST'])
def process() -> Response:
    """
    # TODO what does this do?
    """
    data = request.get_json()
    df = pd.DataFrame(data)
    # Perform preprocessing here
    result = df.describe().to_dict()
    return jsonify(result)


def main() -> None:
    """
    Main function, entrypoint of Flask app.
    """
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
