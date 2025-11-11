"""
Helper utilities for the student dropout prediction application.
Contains common helper functions used across the application.
"""

import os
from typing import Dict, Any, List
import json


def get_project_root() -> str:
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_file_path(filename: str) -> str:
    """Get the full path to a data file in the project root."""
    return os.path.join(get_project_root(), filename)


def format_risk_category(risk: str) -> Dict[str, str]:
    """
    Format risk category with appropriate styling information.
    
    Args:
        risk: Risk category string (Red, Yellow, Green)
        
    Returns:
        Dictionary with formatted risk information
    """
    risk_lower = str(risk).strip().lower()
    
    risk_info = {
        'red': {
            'label': 'Red',
            'description': 'Required mentorship',
            'color': 'red',
            'bg_color': 'bg-red-600',
            'text_color': 'text-red-600'
        },
        'yellow': {
            'label': 'Yellow',
            'description': 'Requires small attention',
            'color': 'yellow',
            'bg_color': 'bg-yellow-500',
            'text_color': 'text-yellow-600'
        },
        'green': {
            'label': 'Green',
            'description': 'Performance is better',
            'color': 'green',
            'bg_color': 'bg-green-600',
            'text_color': 'text-green-600'
        }
    }
    
    return risk_info.get(risk_lower, {
        'label': 'Unknown',
        'description': 'Unknown risk level',
        'color': 'gray',
        'bg_color': 'bg-gray-500',
        'text_color': 'text-gray-600'
    })


def calculate_risk_percentage(probability: float) -> str:
    """
    Calculate risk percentage from probability.
    
    Args:
        probability: Probability value between 0 and 1
        
    Returns:
        Formatted percentage string
    """
    return f"{round(probability * 100, 2)}%"


def get_risk_level_from_probability(probability: float) -> str:
    """
    Get risk level from probability value.
    
    Args:
        probability: Probability value between 0 and 1
        
    Returns:
        Risk level string (Red, Yellow, Green)
    """
    if probability >= 0.66:
        return 'Red'
    elif probability >= 0.33:
        return 'Yellow'
    else:
        return 'Green'


def sort_students_by_risk(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort students by risk category (Red first, then Yellow, then Green).
    
    Args:
        students: List of student dictionaries
        
    Returns:
        Sorted list of students
    """
    def risk_rank(student):
        risk = str(student.get('Risk_Category', '')).strip().lower()
        if risk == 'red':
            return 0
        elif risk == 'yellow':
            return 1
        elif risk == 'green':
            return 2
        else:
            return 3
    
    return sorted(students, key=risk_rank)


def filter_students_by_name(students: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """
    Filter students by name containing search term.
    
    Args:
        students: List of student dictionaries
        search_term: Search term to filter by
        
    Returns:
        Filtered list of students
    """
    if not search_term.strip():
        return students
        
    search_lower = search_term.strip().lower()
    return [
        student for student in students
        if search_lower in str(student.get('Name', '')).lower()
    ]


def create_student_summary(student: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a summary of student information for display.
    
    Args:
        student: Student data dictionary
        
    Returns:
        Summary dictionary with formatted information
    """
    return {
        'name': student.get('Name', 'Unknown'),
        'gender': 'Male' if student.get('Gender') == 'M' else 'Female',
        'age': student.get('Age', 'N/A'),
        'absences': student.get('Number_of_Absences', student.get('Absences', 'N/A')),
        'grade': student.get('Aggregate_Grade', student.get('Final_Grade', student.get('Grade_2', student.get('Grade_1', 'N/A')))),
        'risk_category': student.get('Risk_Category', 'Unknown'),
        'risk_description': student.get('Risk_Description', ''),
        'risk_info': format_risk_category(student.get('Risk_Category', ''))
    }


def generate_student_names(count: int) -> List[str]:
    """
    Generate human-friendly student names.
    
    Args:
        count: Number of names to generate
        
    Returns:
        List of generated names
    """
    first_names = [
        'Aarav', 'Aditi', 'Arjun', 'Isha', 'Kabir', 'Kavya', 'Rohan', 'Saanvi', 'Vihaan', 'Zara',
        'Ananya', 'Dev', 'Ira', 'Meera', 'Neel', 'Reyansh', 'Sara', 'Tara', 'Veda', 'Yash'
    ]
    last_names = [
        'Sharma', 'Verma', 'Patel', 'Iyer', 'Mukherjee', 'Gupta', 'Kapoor', 'Singh', 'Khan', 'Das',
        'Bose', 'Ghosh', 'Mehta', 'Varma', 'Nair', 'Kulkarni', 'Chopra', 'Reddy', 'Jain', 'Tripathi'
    ]
    
    names = []
    for i in range(count):
        fn = first_names[i % len(first_names)]
        ln = last_names[i % len(last_names)]
        names.append(f"{fn} {ln}")
    
    return names


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely load JSON string with fallback to default value.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = '{}') -> str:
    """
    Safely dump data to JSON string with fallback to default.
    
    Args:
        data: Data to serialize
        default: Default string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default
