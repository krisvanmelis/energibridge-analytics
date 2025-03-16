import json
import os

import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect

from dashboards import generate_dashboard
from visualizations import VisualizationConfig, VisualizationType

app = Flask(__name__)


# Sample list to store configurations
configs = [
    VisualizationConfig("Power Analysis", VisualizationType.DELTA_OVER_TIME, "csv-data/preprocessing_output/result_processed.csv"),
]
# Path where Grafana dashboard config will be saved
DASHBOARD_CONFIG_PATH = '../var/lib/grafana/dashboards/test_config.json'
GRAFANA_URL = 'http://localhost:3000'


@app.route('/')
def home():
    """
    Endpoint to render home page where visualizations can be configured.
    """
    return render_template('index.html', configs=configs)


@app.route('/add_config', methods=['POST'])
def add_config():
    """
    Endpoint to add new config to the dashboard.
    """
    data = request.form
    new_config = VisualizationConfig(data['name'], VisualizationType(int(data['kind'])), data['csv_path'])
    configs.append(new_config)
    return jsonify({'status': 'success', 'configs': [c.to_dict() for c in configs]})


@app.route('/delete_config', methods=['POST'])
def delete_config():
    """
    Endpoint to delete a config from the dashboard.
    """
    config_name = request.form['name']
    global configs
    configs = [c for c in configs if c.name != config_name]
    return jsonify({'status': 'success', 'configs': [c.to_dict() for c in configs]})


@app.route('/generate_visualizations')
def generate_visualizations():
    """
    Endpoint to generate visualizations (and grafana dashboard configuration).
    Also redirects to Grafana.
    """
    # Example visualization logic
    if not configs:
        return "No configurations available to visualize.", 400

    # Generate and save json file which configures Grafana dashboard.
    grafana_config = generate_dashboard(configs)
    dir_name = os.path.dirname(DASHBOARD_CONFIG_PATH)
    if not os.path.exists(dir_name):
      os.makedirs(dir_name)
      print(f"Directory '{dir_name}' created.")
    else:
      print(f"Directory '{dir_name}' already exists.")
    with open(DASHBOARD_CONFIG_PATH, 'w') as json_file:
        json.dump(grafana_config, json_file, indent=4)  # `indent=4` for pretty formatting

    print("Grafana dashboard configurations generated.")

    return redirect(GRAFANA_URL)


@app.route('/get_configs', methods=['GET'])
def get_configs():
    """
    Endpoint to get all configs from the dashboard.
    """
    return jsonify([c.to_dict() for c in configs])


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    df = pd.DataFrame(data)
    # Perform preprocessing here
    result = df.describe().to_dict()
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
