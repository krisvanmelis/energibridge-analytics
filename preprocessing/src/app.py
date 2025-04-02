"""
Flask application for generating Grafana dashboard configurations.
Provides API endpoints for managing experiments and generating visualizations.
"""
import json
import logging
import os

from flask import Flask, jsonify, request, render_template, redirect, Response

from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType
from group_service import GroupService
from experiment_service import ExperimentService
from grafana_service import GrafanaService

# Path where Grafana dashboard config will be saved
DASHBOARD_CONFIG_SAVE_PATH = 'grafana/dashboards/energibridge-dashboard.json'
GRAFANA_URL = 'http://localhost:3000'

# Initialize Flask application and services
app = Flask(__name__)
group_service = GroupService()
experiment_service = ExperimentService(group_service)
grafana_service = GrafanaService(DASHBOARD_CONFIG_SAVE_PATH)


@app.route('/')
def home() -> str:
    """
    Endpoint to render home page where visualizations can be configured.

    :return: Rendered home page
    """
    return render_template('index.html', experiments=experiment_service.get_experiments())


@app.route('/groups')
def get_groups() -> Response:
    """
    Endpoint to fetch all groups.
    """
    return jsonify({'status': 'success', 'groups': [group.to_dict() for group in group_service.get_groups()]})

@app.route('/experiments')
def get_experiments() -> Response:
    """
    Endpoint to get all experiment configs.

    :return: JSON response with all experiments
    """
    return jsonify({'status': 'success', 'experiments': [exp.to_dict() for exp in experiment_service.get_experiments()]})


@app.route('/experiments', methods=['POST'])
def add_experiment() -> Response:
    """
    Endpoint to add new experiment.

    :return: JSON response with new experiments list
    """
    try:
        data = json.loads(request.json)
        name = data['name']
        group_names = data['group_names']
        
        # Log received data for debugging
        app.logger.debug(f"Received experiment data: {data}")
        app.logger.debug(f"Measurement types from request: {data['measurement_types']}")
        app.logger.debug(f"Available MeasurementType values: {[(mt.name, mt.value) for mt in MeasurementType]}")
        
        # Convert measurement types with enhanced error handling focusing on tuple first value
        measurement_types = []
        valid_values = {}
        
        # Build a map of valid enum values for easier lookup
        for mt in MeasurementType:
            valid_values[mt.value] = mt
            
        app.logger.debug(f"Valid measurement type values map: {valid_values}")
        
        for mt_value in data['measurement_types']:
            try:
                mt_int = int(mt_value)
                # Check if the integer value exists in our valid values map
                if mt_int in valid_values:
                    measurement_type = valid_values[mt_int]
                    measurement_types.append(measurement_type)
                    app.logger.debug(f"Successfully matched {mt_int} to {measurement_type}")
                else:
                    app.logger.error(f"Value {mt_int} not found in MeasurementType enum values")
                    return jsonify({
                        'status': 'error', 
                        'message': f"Value {mt_int} is not a valid measurement type",
                        'valid_values': list(valid_values.keys())
                    })
            except Exception as e:
                app.logger.error(f"Error converting measurement type {mt_value}: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error', 
                    'message': f"Error processing measurement type {mt_value}: {str(e)}",
                    'valid_values': list(valid_values.keys())
                })
                
        experiment_type = ExperimentType(int(data['experiment_type']))

        experiments = experiment_service.add_experiment(name, group_names, measurement_types, experiment_type)
        return jsonify({'status': 'success', 'experiments': [exp.to_dict() for exp in experiments]})
    except Exception as e:
        app.logger.error(f"Error adding experiment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/experiments', methods=['DELETE'])
def delete_experiment() -> Response:
    """
    Endpoint to delete an experiment.

    :return: JSON response with new experiments list
    """
    request_json = request.get_json()
    experiment_name = request_json['name']

    try:
        return jsonify({'status': 'success', 'experiments': [exp.to_dict() for exp in experiment_service.delete_experiment(experiment_name)]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/visualizations/generate')
def generate_visualizations() -> Response:
    """
    Generate a Grafana dashboard with visualizations for all experiments.
    Creates panels for each experiment and measurement type and saves the dashboard config.

    :return: JSON response with success message.
    """
    experiments = experiment_service.get_experiments()
    app.logger.info(f'Generating visualizations for experiments: {experiments}')

    # Create dashboard using the GrafanaService
    grafana_service.create_dashboard_from_experiments(experiments)

    return jsonify({'status': 'success', 'message': 'Visualizations generated successfully!'})


@app.route('/csv-data/input/')
def get_folder_paths() -> Response:
    """
    Endpoint to get all folder paths in input folder.
    """
    return jsonify({'folders': [f for f in os.listdir('csv-data/input') if os.path.isdir(os.path.join('csv-data/input', f))]})


@app.route('/measurement-types', methods=['GET'])
def get_measurement_types():
    """
    Get available measurement types for experiments, filtered by experiment type if provided.
    """
    try:
        # Check if an experiment type filter was provided
        experiment_type_id = request.args.get('experiment_type')
        
        # Convert measurement types to a list of dictionaries for the frontend
        if experiment_type_id:
            # Filter measurement types by experiment type
            try:
                experiment_type = ExperimentType(int(experiment_type_id))
                measurement_types = MeasurementType.get_compatible_types(experiment_type)
            except (ValueError, TypeError):
                # If the experiment_type_id is invalid, return all measurement types
                measurement_types = list(MeasurementType)
        else:
            # No filter, return all measurement types
            measurement_types = list(MeasurementType)
        
        # Skip the "ALL" type for the frontend
        measurement_types = [mt for mt in measurement_types if mt != MeasurementType.ALL]
        
        # Convert to JSON-serializable format
        types_json = [{"id": mt.value, "name": mt.name} for mt in measurement_types]
        
        return jsonify({
            "status": "success",
            "measurement_types": types_json
        })
    except Exception as e:
        app.logger.error(f"Error getting measurement types: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error getting measurement types: {str(e)}"
        })


def main() -> None:
    """
    Main function, entrypoint of Flask app.
    """
    app.run(host='0.0.0.0', port=5000, reloader=True, debug=True)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s')


if __name__ == '__main__':
    main()
