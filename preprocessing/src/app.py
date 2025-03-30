"""
Module containing Flask application for generating grafana dashboard configurations.
"""
import json
import logging

from flask import Flask, jsonify, request, render_template, redirect, Response

from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType
from group_service import GroupService
from panel_service import PanelService
from grafana_visualization_service import GrafanaVisualizationService

# Path where Grafana dashboard config will be saved
# DASHBOARD_CONFIG_SAVE_PATH = '../var/lib/grafana/dashboards/test_config.json'
DASHBOARD_CONFIG_SAVE_PATH = '../var/lib/grafana/dashboards/test_config4.json'

GRAFANA_URL = 'http://localhost:3000'

app = Flask(__name__)
group_service = GroupService()
panel_service = PanelService(group_service)
grafana_visualization_service = GrafanaVisualizationService(DASHBOARD_CONFIG_SAVE_PATH)


@app.route('/')
def home() -> str:
    """
    Endpoint to render home page where visualizations can be configured.

    :return: Rendered home page
    """
    return render_template('index.html', panels=panel_service.get_panels())


@app.route('/groups')
def get_groups() -> Response:
    """
    Endpoint to fetch all groups.
    """
    return jsonify({'status': 'success', 'groups': [group.to_dict() for group in group_service.get_groups()]})


@app.route('/groups', methods=['POST'])
def add_group() -> Response:
    """
    Endpoint to add a new group.
    Returns error if group with name already exists or folder not found.

    :return: Response with new list of groups.
    """
    data = request.get_json()
    name = data['name']
    folder_path = data['folder_path']

    try:
        groups = group_service.add_group(name, folder_path)
        return jsonify({'status': 'success', 'groups': [group.to_dict() for group in groups]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/groups', methods=['DELETE'])
def delete_group() -> Response:
    """
    Endpoint to delete a group by name.

    :return: Response with new list of groups.
    """
    request_json = request.get_json()
    group_name = request_json['name']

    try:
        return jsonify({'status': 'success', 'groups': [group.to_dict() for group in group_service.delete_group(group_name)]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/panels')
def get_panels() -> Response:
    """
    Endpoint to get all panel configs from the dashboard.

    :return: JSON response with all configs
    """
    return jsonify({'status': 'success', 'panels': [panel.to_dict() for panel in panel_service.get_panels()]})


@app.route('/panels', methods=['POST'])
def add_panel() -> Response:
    """
    Endpoint to add new panel config to the dashboard.

    :return: JSON response with new configs list
    """
    data = json.loads(request.json)
    name = data['name']
    group_names = data['group_names']
    measurement_types = [MeasurementType(int(measurement_type)) for measurement_type in data['measurement_types']]
    experiment_type = ExperimentType(int(data['experiment_type']))

    try:
        return jsonify({'status': 'success', 'panels': [panel.to_dict() for panel in panel_service.add_panel(name, group_names, measurement_types, experiment_type)]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/panels', methods=['DELETE'])
def delete_panel() -> Response:
    """
    Endpoint to delete a panel config from the dashboard.

    :return: JSON response with new configs
    """
    request_json = request.get_json()
    panel_name = request_json['name']

    try:
        return jsonify({'status': 'success', 'panels': [panel.to_dict() for panel in panel_service.delete_panel(panel_name)]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/visualizations/generate')
def generate_visualizations() -> Response:
    """
    Endpoint to generate visualizations (and grafana dashboard configuration).
    Also redirects to Grafana.

    :return: JSON response with redirect
    """
    panel_configs = panel_service.get_panels()
    app.logger.info(f'Following config asked for: {panel_configs}')

    grafana_visualization_service.configure(panel_configs)

    return redirect(GRAFANA_URL)


def main() -> None:
    """
    Main function, entrypoint of Flask app.
    """
    app.run(host='0.0.0.0', port=5001)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG,  # Log all levels (DEBUG, INFO, etc.)
                        format='%(asctime)s [%(levelname)s] %(message)s')


if __name__ == '__main__':
    main()
