"""
API routes for the student dropout prediction application.
Handles all API endpoints for data operations and predictions.
"""

from flask import jsonify, request, make_response
from models.data_handler import DataHandler
from models.ml_model import MLModel


def register_api_routes(app, data_handler: DataHandler, ml_model: MLModel):
    """Register API routes with the Flask app."""
    
    @app.route('/add_student', methods=['POST'])
    def add_student():
        """Add a new student to the in-memory dataset and rewrite the JSON."""
        try:
            data = request.json or {}
            
            # Input validation
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'error': 'Name is required'}), 400
                
            gender = (data.get('gender') or 'M').strip().upper()
            if gender not in ('M', 'F'):
                return jsonify({'error': 'Gender must be M or F'}), 400
                
            try:
                age = int(data.get('age', 18))
            except (ValueError, TypeError):
                return jsonify({'error': 'Age must be an integer'}), 400
            if age < 10 or age > 60:
                return jsonify({'error': 'Age must be between 10 and 60'}), 400
                
            try:
                absences = int(data.get('absences', 0))
            except (ValueError, TypeError):
                return jsonify({'error': 'Absences must be an integer'}), 400
            if absences < 0 or absences > 365:
                return jsonify({'error': 'Absences must be between 0 and 365'}), 400
                
            try:
                agg = float(data.get('aggregate_grade', 12))
            except (ValueError, TypeError):
                return jsonify({'error': 'Aggregate grade must be a number'}), 400
            if agg < 0 or agg > 20:
                return jsonify({'error': 'Aggregate grade must be between 0 and 20'}), 400
                
            internet = str(data.get('internet_access', 'yes')).strip().lower()
            if internet not in ('yes', 'no'):
                return jsonify({'error': 'Internet access must be yes or no'}), 400
                
            desired_zone = (data.get('desired_risk_zone') or '').strip()
            if desired_zone and desired_zone not in ('Red', 'Yellow', 'Green'):
                return jsonify({'error': 'Desired risk zone must be Red, Yellow, or Green'}), 400

            # Get prediction from ML model
            prob, predicted_risk, risk_desc = ml_model.predict_dropout_probability(data)
            
            # Enforce desired risk zone if provided (constraint)
            if desired_zone in ['Red', 'Yellow', 'Green']:
                risk_cat = desired_zone
            else:
                risk_cat = predicted_risk
                
            # Add risk information to student data
            data['risk_category'] = risk_cat
            data['risk_description'] = risk_desc
            data['risk_score'] = round(prob * 100, 2)

            # Add student to dataset
            row = data_handler.add_student(data)
            
            return jsonify({
                'status': 'ok', 
                'risk_category': risk_cat, 
                'probability': round(prob * 100, 2)
            })
            
        except Exception as e:
            app.logger.error(f"Add student error: {e}")
            return jsonify({'error': str(e)}), 400

    @app.route('/students')
    def students():
        """Return the latest 100 students with names and risk info (tail)."""
        records = data_handler.get_students_list(100)
        resp = make_response(jsonify(records))
        resp.headers['Cache-Control'] = 'no-store'
        return resp

    @app.route('/risk_summary')
    def risk_summary():
        """Return counts for red/yellow/green and total students."""
        try:
            summary = data_handler.get_risk_summary()
            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/predict', methods=['POST'])
    def predict():
        """API endpoint for receiving student data and returning a prediction."""
        try:
            data = request.json
            result = ml_model.predict_from_form_data(data)
            return jsonify(result)
        except Exception as e:
            app.logger.error(f"Prediction error: {e}")
            return jsonify({'error': str(e), 'message': 'Invalid input data or server error.'}), 400

    @app.route('/dashboard_data')
    def dashboard_data():
        """API endpoint to fetch data required for dashboard charts."""
        try:
            dashboard_data = data_handler.get_dashboard_data()
            return jsonify(dashboard_data)
        except Exception as e:
            app.logger.error(f"Dashboard data error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/delete_student', methods=['POST'])
    def delete_student():
        """Delete a student by index or by name (first match)."""
        try:
            data = request.json or {}
            idx = data.get('index')
            name = (data.get('name') or '').strip()

            deleted_label = None
            if idx is not None and str(idx) != '':
                try:
                    i = int(idx)
                    deleted_label = data_handler.delete_student(index=i)
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid index'}), 400
            elif name:
                try:
                    deleted_label = data_handler.delete_student(name=name)
                except ValueError as e:
                    return jsonify({'error': str(e)}), 404
            else:
                return jsonify({'error': 'Provide index or name'}), 400

            return jsonify({'status': 'ok', 'deleted': deleted_label})
            
        except Exception as e:
            app.logger.error(f"Delete student error: {e}")
            return jsonify({'error': str(e)}), 400
