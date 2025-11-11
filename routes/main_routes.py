"""
Main routes for the student dropout prediction application.
Handles home page, dashboard, and basic navigation.
"""

from flask import render_template, jsonify, request, make_response
from models.data_handler import DataHandler
from models.ml_model import MLModel


def register_main_routes(app, data_handler: DataHandler, ml_model: MLModel):
    """Register main routes with the Flask app."""
    
    @app.route('/')
    def home():
        """Serves the homepage with Add Student and Quick Predictor."""
        return render_template('home.html')

    @app.route('/dashboard')
    def dashboard():
        """Serves the interactive dashboard page."""
        return render_template('dashboard.html')

    @app.route('/students_view')
    def students_view():
        """Serves the students list view page."""
        return render_template('students_view.html')

    @app.route('/print_report')
    def print_report():
        """Serves the printable report page."""
        return render_template('print_report.html')

    @app.route('/edit_student', methods=['GET', 'POST'])
    def edit_student():
        """Edit a student by index. GET serves form, POST updates the record.
        Supports both 'index' (visible order) and 'gindex' (global DataFrame index).
        """
        # Prefer global index if provided
        if request.method == 'GET':
            idx_str = request.args.get('gindex') or request.args.get('index')
        else:
            body = request.json or {}
            idx_str = request.args.get('gindex') or request.args.get('index') or body.get('gindex') or body.get('index')
            
        try:
            if idx_str is None:
                return jsonify({'error': 'index is required'}), 400
            idx = int(idx_str)
            if idx < 0 or idx >= len(data_handler.students_df):
                return jsonify({'error': 'index out of range'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'invalid index'}), 400

        if request.method == 'GET':
            s = data_handler.students_df.iloc[[idx]].to_dict('records')[0]
            return render_template('edit_student.html', 
                                 idx=idx, 
                                 name=str(s.get('Name', '')),
                                 gender=s.get('Gender', ''),
                                 age=s.get('Age', ''),
                                 absences=s.get('Number_of_Absences', s.get('Absences', '')),
                                 aggregate=s.get('Aggregate_Grade', s.get('Final_Grade', s.get('Grade_2', s.get('Grade_1', '')))),
                                 internet=str(s.get('Internet_Access', '')).lower())

        # POST: update record
        try:
            data = request.json or {}
            data_handler.update_student(idx, data)
            return jsonify({'status': 'ok'})
        except Exception as e:
            app.logger.error(f"Edit student error: {e}")
            return jsonify({'error': str(e)}), 400
