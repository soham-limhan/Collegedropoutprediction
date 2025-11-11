"""
Configuration settings for the student dropout prediction application.
Contains all application settings and constants.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File paths
    CSV_FILENAME = 'student_dropout_with_risk.csv'
    JSON_OUTPUT_FILENAME = 'students_100.json'
    
    # Data settings
    DEFAULT_STUDENT_LIMIT = 100
    MIN_RED_STUDENTS = 5
    
    # Validation limits
    MIN_AGE = 10
    MAX_AGE = 60
    MIN_ABSENCES = 0
    MAX_ABSENCES = 365
    MIN_GRADE = 0
    MAX_GRADE = 20
    MIN_GPA = 0.0
    MAX_GPA = 4.0
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 0.66
    MEDIUM_RISK_THRESHOLD = 0.33
    
    # Model settings
    MODEL_RANDOM_STATE = 42
    MODEL_SOLVER = 'liblinear'
    
    # Chart settings
    CHART_COLORS = {
        'red': '#ef4444',
        'yellow': '#f59e0b',
        'green': '#10b981',
        'blue': '#3b82f6',
        'emerald': '#10b981'
    }
    
    # Student names for generation
    FIRST_NAMES = [
        'Aarav', 'Aditi', 'Arjun', 'Isha', 'Kabir', 'Kavya', 'Rohan', 'Saanvi', 'Vihaan', 'Zara',
        'Ananya', 'Dev', 'Ira', 'Meera', 'Neel', 'Reyansh', 'Sara', 'Tara', 'Veda', 'Yash'
    ]
    
    LAST_NAMES = [
        'Sharma', 'Verma', 'Patel', 'Iyer', 'Mukherjee', 'Gupta', 'Kapoor', 'Singh', 'Khan', 'Das',
        'Bose', 'Ghosh', 'Mehta', 'Varma', 'Nair', 'Kulkarni', 'Chopra', 'Reddy', 'Jain', 'Tripathi'
    ]
    
    # Risk descriptions
    RISK_DESCRIPTIONS = {
        'red': 'Required mentorship',
        'yellow': 'Requires small attention',
        'green': 'Performance is better',
        'unknown': 'Unknown'
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])


def get_file_paths() -> Dict[str, str]:
    """
    Get file paths for data files.
    
    Returns:
        Dictionary with file paths
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return {
        'csv_file': os.path.join(base_dir, Config.CSV_FILENAME),
        'json_file': os.path.join(base_dir, Config.JSON_OUTPUT_FILENAME)
    }


def get_validation_limits() -> Dict[str, Any]:
    """
    Get validation limits for form inputs.
    
    Returns:
        Dictionary with validation limits
    """
    return {
        'age': {'min': Config.MIN_AGE, 'max': Config.MAX_AGE},
        'absences': {'min': Config.MIN_ABSENCES, 'max': Config.MAX_ABSENCES},
        'grade': {'min': Config.MIN_GRADE, 'max': Config.MAX_GRADE},
        'gpa': {'min': Config.MIN_GPA, 'max': Config.MAX_GPA}
    }


def get_risk_thresholds() -> Dict[str, float]:
    """
    Get risk assessment thresholds.
    
    Returns:
        Dictionary with risk thresholds
    """
    return {
        'high_risk': Config.HIGH_RISK_THRESHOLD,
        'medium_risk': Config.MEDIUM_RISK_THRESHOLD
    }
