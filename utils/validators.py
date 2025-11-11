"""
Validation utilities for the student dropout prediction application.
Contains input validation functions for student data.
"""

from typing import Dict, Any, Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_student_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate student data for adding/updating students.
    
    Args:
        data: Dictionary containing student data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate name
        name = (data.get('name') or '').strip()
        if not name:
            return False, 'Name is required'
            
        # Validate gender
        gender = (data.get('gender') or 'M').strip().upper()
        if gender not in ('M', 'F'):
            return False, 'Gender must be M or F'
            
        # Validate age
        try:
            age = int(data.get('age', 18))
        except (ValueError, TypeError):
            return False, 'Age must be an integer'
        if age < 10 or age > 60:
            return False, 'Age must be between 10 and 60'
            
        # Validate absences
        try:
            absences = int(data.get('absences', 0))
        except (ValueError, TypeError):
            return False, 'Absences must be an integer'
        if absences < 0 or absences > 365:
            return False, 'Absences must be between 0 and 365'
            
        # Validate aggregate grade
        try:
            agg = float(data.get('aggregate_grade', 12))
        except (ValueError, TypeError):
            return False, 'Aggregate grade must be a number'
        if agg < 0 or agg > 20:
            return False, 'Aggregate grade must be between 0 and 20'
            
        # Validate internet access
        internet = str(data.get('internet_access', 'yes')).strip().lower()
        if internet not in ('yes', 'no'):
            return False, 'Internet access must be yes or no'
            
        # Validate desired risk zone
        desired_zone = (data.get('desired_risk_zone') or '').strip()
        if desired_zone and desired_zone not in ('Red', 'Yellow', 'Green'):
            return False, 'Desired risk zone must be Red, Yellow, or Green'
            
        return True, None
        
    except Exception as e:
        return False, f'Validation error: {str(e)}'


def validate_prediction_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate prediction form data.
    
    Args:
        data: Dictionary containing prediction data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate age
        try:
            age = float(data.get('age', 20))
            if age < 18 or age > 60:
                return False, 'Age must be between 18 and 60'
        except (ValueError, TypeError):
            return False, 'Age must be a number'
            
        # Validate GPA
        try:
            gpa = float(data.get('gpa', 3.0))
            if gpa < 0 or gpa > 4.0:
                return False, 'GPA must be between 0.0 and 4.0'
        except (ValueError, TypeError):
            return False, 'GPA must be a number'
            
        # Validate absences
        try:
            absences = float(data.get('absences', 5))
            if absences < 0:
                return False, 'Absences must be non-negative'
        except (ValueError, TypeError):
            return False, 'Absences must be a number'
            
        # Validate study hours
        try:
            study_hours = float(data.get('study_hours', 20))
            if study_hours < 0:
                return False, 'Study hours must be non-negative'
        except (ValueError, TypeError):
            return False, 'Study hours must be a number'
            
        # Validate gender
        gender = data.get('gender', 'F')
        if gender not in ('M', 'F'):
            return False, 'Gender must be M or F'
            
        # Validate financial aid
        try:
            financial_aid = float(data.get('financial_aid', 0))
            if financial_aid not in (0, 1):
                return False, 'Financial aid must be 0 or 1'
        except (ValueError, TypeError):
            return False, 'Financial aid must be 0 or 1'
            
        return True, None
        
    except Exception as e:
        return False, f'Validation error: {str(e)}'


def validate_index(index_str: str, max_index: int) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate index parameter.
    
    Args:
        index_str: String representation of index
        max_index: Maximum valid index
        
    Returns:
        Tuple of (is_valid, index_value, error_message)
    """
    try:
        if index_str is None:
            return False, None, 'Index is required'
            
        idx = int(index_str)
        if idx < 0 or idx >= max_index:
            return False, None, 'Index out of range'
            
        return True, idx, None
        
    except (ValueError, TypeError):
        return False, None, 'Invalid index'


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data by trimming strings and converting types.
    
    Args:
        data: Raw input data
        
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
            
    return sanitized
