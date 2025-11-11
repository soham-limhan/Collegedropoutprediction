# Student Dropout Prediction System - Modular Version

A Flask web application for predicting college student dropout risk using machine learning. This modular version provides better code organization, maintainability, and scalability.

## Project Structure

```
├── app.py                 # Original monolithic application
├── app_new.py            # New modular application entry point
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── config/              # Configuration settings
│   ├── __init__.py
│   └── settings.py      # App configuration and constants
├── models/              # Data handling and ML operations
│   ├── __init__.py
│   ├── data_handler.py  # CSV/JSON operations and data management
│   └── ml_model.py      # Machine learning model and predictions
├── routes/              # Flask route handlers
│   ├── __init__.py
│   ├── main_routes.py   # Main page routes (home, dashboard, etc.)
│   └── api_routes.py    # API endpoints for data operations
├── templates/           # HTML templates
│   ├── home.html        # Homepage template
│   ├── dashboard.html   # Dashboard template
│   ├── students_view.html # Students list template
│   ├── print_report.html # Report template
│   └── edit_student.html # Edit student template
├── static/              # Static assets
│   ├── css/            # CSS files (if any)
│   └── js/             # JavaScript files
│       ├── home.js     # Homepage JavaScript
│       ├── dashboard.js # Dashboard JavaScript
│       ├── students_view.js # Students view JavaScript
│       └── print_report.js # Report JavaScript
├── utils/               # Helper functions and utilities
│   ├── __init__.py
│   ├── helpers.py       # Common helper functions
│   └── validators.py    # Input validation functions
└── data files/          # Data files (CSV, JSON)
    ├── student_dropout_with_risk.csv
    └── students_100.json
```

## Features

### Core Functionality
- **Student Management**: Add, edit, delete, and view students
- **Risk Prediction**: ML-based dropout risk assessment
- **Interactive Dashboard**: Visual analytics and charts
- **Report Generation**: Printable reports for individual or all students
- **Data Export**: JSON export of student data

### Machine Learning
- **Logistic Regression Model**: Trained on student features
- **Risk Categorization**: Red (High), Yellow (Medium), Green (Low) risk levels
- **Feature Engineering**: Age, GPA, absences, study hours, gender, financial aid

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS
- **Interactive Charts**: Chart.js for data visualization
- **Real-time Updates**: Dynamic content updates without page refresh

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure data files are present**:
   - `student_dropout_with_risk.csv` - Main dataset
   - The application will create `students_100.json` automatically

4. **Run the application**:
   ```bash
   python app_new.py
   ```

5. **Access the application**:
   - Homepage: http://127.0.0.1:5000/
   - Dashboard: http://127.0.0.1:5000/dashboard

## Usage

### Homepage (`/`)
- View overall risk summary with charts
- Add new students with risk prediction
- Quick dropout risk predictor
- Access to all main features via menu

### Dashboard (`/dashboard`)
- Interactive risk prediction tool
- Browse and view individual student details
- Analytics charts (gender-based dropout rates, absence patterns)
- Student selector with detailed information

### Student Management
- **View Students** (`/students_view`): Complete list with search and filtering
- **Add Student**: Form with validation and automatic risk assessment
- **Edit Student**: Modify existing student information
- **Delete Student**: Remove students by index or name

### Reports
- **Print Reports** (`/print_report`): Generate printable reports
- Individual student reports or full dataset reports
- Risk summary statistics

## API Endpoints

### Data Operations
- `POST /add_student` - Add new student
- `GET /students` - Get student list
- `POST /edit_student` - Update student
- `POST /delete_student` - Delete student

### Analytics
- `GET /risk_summary` - Get risk category counts
- `GET /dashboard_data` - Get dashboard chart data

### Predictions
- `POST /predict` - Predict dropout risk from form data

## Configuration

The application uses environment-based configuration:

- **Development**: Default configuration with debug enabled
- **Production**: Optimized for production deployment
- **Testing**: Configuration for unit testing

Key configuration options in `config/settings.py`:
- File paths for data files
- Validation limits for form inputs
- Risk assessment thresholds
- Model training parameters

## Modular Architecture Benefits

### 1. **Separation of Concerns**
- **Models**: Data handling and ML operations isolated
- **Routes**: Web interface logic separated from business logic
- **Templates**: HTML structure separated from Python code
- **Static Files**: CSS/JS assets organized separately

### 2. **Maintainability**
- Each module has a single responsibility
- Easy to locate and modify specific functionality
- Clear dependencies between modules
- Consistent code organization

### 3. **Scalability**
- Easy to add new features without affecting existing code
- Modular structure supports team development
- Configuration management for different environments
- Extensible architecture for future enhancements

### 4. **Testing**
- Individual modules can be tested in isolation
- Mock dependencies for unit testing
- Configuration-based testing setup

### 5. **Reusability**
- Utility functions can be reused across modules
- Data handling logic can be used in different contexts
- ML model can be used independently of web interface

## Development

### Adding New Features
1. **New Routes**: Add to appropriate route module
2. **New Templates**: Create in `templates/` directory
3. **New Static Files**: Add to `static/` directory
4. **New Utilities**: Add to `utils/` directory
5. **Configuration Changes**: Update `config/settings.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes
- Keep modules focused on single responsibilities

## Dependencies

- **Flask**: Web framework
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scikit-learn**: Machine learning
- **Tailwind CSS**: UI styling (CDN)
- **Chart.js**: Data visualization (CDN)

## Future Enhancements

- Database integration (MySQL, PostgreSQL)
- User authentication and authorization
- Advanced ML models (Random Forest, Neural Networks)
- Real-time data updates
- API rate limiting and security
- Docker containerization
- Unit and integration tests
- Logging and monitoring

## Migration from Original

The original `app.py` remains unchanged for reference. The new modular version (`app_new.py`) provides the same functionality with improved organization. To migrate:

1. Use `app_new.py` instead of `app.py`
2. All existing data files and functionality remain compatible
3. No changes needed to existing data or configurations
