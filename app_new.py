"""
Student Dropout Prediction Application - Modular Version
A Flask web application for predicting college student dropout risk using machine learning.

This modular version separates concerns into different modules:
- models/: Data handling and ML operations
- routes/: Flask route handlers
- templates/: HTML templates
- static/: CSS and JavaScript files
- utils/: Helper functions and validators
- config/: Application configuration
"""

import os
from flask import Flask

# Import our custom modules
from models.data_handler import DataHandler
from models.ml_model import MLModel
from routes.main_routes import register_main_routes
from routes.api_routes import register_api_routes
from config.settings import get_config, get_file_paths


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Get file paths
    file_paths = get_file_paths()
    
    # Initialize data handler and ML model
    data_handler = DataHandler(
        csv_filename=file_paths['csv_file'],
        json_filename=file_paths['json_file']
    )
    
    ml_model = MLModel()
    
    # Initialize data and train model
    try:
        print("Initializing data...")
        data_handler.initialize_data(limit=config.DEFAULT_STUDENT_LIMIT)
        
        print("Training ML model...")
        ml_model.train_model(data_handler.dashboard_data)
        
        print(f"Loaded {len(data_handler.students_df)} students from CSV and wrote {config.JSON_OUTPUT_FILENAME}.")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        # Continue with empty data if files don't exist
        if not os.path.exists(file_paths['csv_file']):
            print(f"Warning: CSV file not found at {file_paths['csv_file']}")
        if not os.path.exists(file_paths['json_file']):
            print(f"Warning: JSON file not found at {file_paths['json_file']}")
    
    # Register routes
    register_main_routes(app, data_handler, ml_model)
    register_api_routes(app, data_handler, ml_model)
    
    # Store instances in app context for access in routes
    app.data_handler = data_handler
    app.ml_model = ml_model
    
    return app


def main():
    """Main function to run the application."""
    # Create app instance
    app = create_app()
    
    # Print startup information
    print("=" * 70)
    print("FLASK APP READY: Running Dropout Predictor (Modular Version)")
    print("Access the homepage at: http://127.0.0.1:5000/")
    print("Dashboard at: http://127.0.0.1:5000/dashboard")
    print("=" * 70)
    
    # Run the application
    # In a production environment, you would use a WSGI server (like gunicorn)
    # and properly load the model from a file using joblib or pickle.
    app.run(debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
