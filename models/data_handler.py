"""
Data handling module for student dropout prediction system.
Handles CSV loading, JSON operations, and data preprocessing.
"""

import pandas as pd
import json
import os
from typing import Dict, Any, List


class DataHandler:
    """Handles all data operations for the student dropout prediction system."""
    
    def __init__(self, csv_filename: str, json_filename: str):
        self.csv_filename = csv_filename
        self.json_filename = json_filename
        self.students_df = None
        self.dashboard_data = None
        
    def load_students_from_csv(self, limit: int = 100) -> pd.DataFrame:
        """Load first N students from CSV, ensure a Name column with human-friendly names, 
        include some Red-category students, and return DataFrame."""
        full_df = pd.read_csv(self.csv_filename)
        df = full_df.head(limit).copy()

        # Ensure at least some red-category students are present (target at least 5)
        target_min_red = 5
        risk_col = 'Risk_Category' if 'Risk_Category' in full_df.columns else None
        if risk_col is not None:
            def _norm(val):
                return str(val).strip().lower()
            current_red = df[df[risk_col].apply(_norm) == 'red']
            if len(current_red) < target_min_red:
                needed = target_min_red - len(current_red)
                pool_red = full_df[full_df[risk_col].apply(_norm) == 'red']
                pool_red = pool_red.iloc[limit:] if len(pool_red) > limit else pool_red
                # Exclude rows already in df by index if overlapping
                pool_red = pool_red[~pool_red.index.isin(df.index)]
                if needed > 0 and len(pool_red) > 0:
                    add_rows = pool_red.head(needed)
                    # Replace the last 'needed' non-red rows in df with these red rows
                    non_red_idx = df[df[risk_col].apply(_norm) != 'red'].index.tolist()
                    replace_idx = non_red_idx[-len(add_rows):] if len(non_red_idx) >= len(add_rows) else non_red_idx
                    for rep_i, add_row in zip(replace_idx, add_rows.to_dict(orient='records')):
                        df.loc[rep_i] = add_row

        # Add human-friendly names if missing
        if 'Name' not in df.columns:
            first_names = [
                'Aarav','Aditi','Arjun','Isha','Kabir','Kavya','Rohan','Saanvi','Vihaan','Zara',
                'Ananya','Dev','Ira','Meera','Neel','Reyansh','Sara','Tara','Veda','Yash'
            ]
            last_names = [
                'Sharma','Verma','Patel','Iyer','Mukherjee','Gupta','Kapoor','Singh','Khan','Das',
                'Bose','Ghosh','Mehta','Varma','Nair','Kulkarni','Chopra','Reddy','Jain','Tripathi'
            ]
            names = []
            for i in range(len(df)):
                fn = first_names[i % len(first_names)]
                ln = last_names[i % len(last_names)]
                names.append(f"{fn} {ln}")
            df['Name'] = names

        # Add risk description mapping column for convenience
        if risk_col is not None:
            def describe_risk(val: str) -> str:
                v = str(val).strip().lower()
                if v == 'red':
                    return 'Required mentorship'
                if v == 'yellow':
                    return 'Requires small attention'
                if v == 'green':
                    return 'Performance is better'
                return 'Unknown'
            df['Risk_Description'] = df[risk_col].apply(describe_risk)

        return df

    def write_students_json(self, df: pd.DataFrame) -> None:
        """Write the given DataFrame to a JSON file (records orientation)."""
        # Ensure native JSON types
        records = json.loads(df.to_json(orient='records'))
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def initialize_data(self, limit: int = 100) -> None:
        """Initialize the data by loading from CSV and creating JSON."""
        self.students_df = self.load_students_from_csv(limit)
        self.write_students_json(self.students_df)
        
        # Prepare dashboard data from CSV columns
        self.dashboard_data = self.students_df.copy()
        
        # Compute a binary dropout flag from Dropped_Out (Yes/No) if available
        if 'Dropped_Out' in self.dashboard_data.columns:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes'
            ).astype(int)
        else:
            # Fallback: derive from Risk_Category (treat Red as high-risk ~ dropout)
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Risk_Category'].astype(str).str.strip().str.lower() == 'red'
            ).astype(int)

    def add_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new student to the dataset."""
        # Build a single-row frame from incoming data, mapping to CSV-like columns
        row = {}
        # Basic columns
        row['Name'] = student_data.get('name') or f"Student {len(self.students_df)+1}"
        row['Gender'] = student_data.get('gender', 'M')
        row['Age'] = int(student_data.get('age', 18))
        row['Number_of_Absences'] = int(student_data.get('absences', 0))
        
        # Single aggregate grade replaces G1/G2/Final_Grade
        agg = float(student_data.get('aggregate_grade', 12))
        row['Aggregate_Grade'] = agg
        # For backwards compatibility fields if other code expects them
        row['Grade_1'] = agg
        row['Grade_2'] = agg
        row['Final_Grade'] = agg
        row['Internet_Access'] = str(student_data.get('internet_access', 'yes')).lower()
        row['School'] = student_data.get('school', 'GP')
        row['Address'] = student_data.get('address', 'U')
        row['Family_Size'] = student_data.get('family_size', 'GT3')
        row['Parental_Status'] = student_data.get('parental_status', 'T')
        row['Mother_Education'] = student_data.get('mother_education', 2)
        row['Father_Education'] = student_data.get('father_education', 2)
        row['Travel_Time'] = student_data.get('travel_time', 1)
        row['Study_Time'] = student_data.get('study_time', 2)
        row['Number_of_Failures'] = student_data.get('number_of_failures', 0)
        row['Health_Status'] = student_data.get('health_status', 3)

        # Append to STUDENTS_DF
        self.students_df = pd.concat([self.students_df, pd.DataFrame([row])], ignore_index=True)
        
        # Update dashboard data
        self.dashboard_data = self.students_df.copy()
        if 'Dropped_Out' in self.dashboard_data.columns:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes'
            ).astype(int)
        else:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Risk_Category'].astype(str).str.strip().str.lower() == 'red'
            ).astype(int)

        # Rewrite JSON with full dataset
        self.write_students_json(self.students_df)
        
        return row

    def update_student(self, index: int, student_data: Dict[str, Any]) -> None:
        """Update an existing student in the dataset."""
        # Update basic fields
        if 'name' in student_data:
            self.students_df.at[index, 'Name'] = student_data['name']
        if 'gender' in student_data:
            self.students_df.at[index, 'Gender'] = student_data['gender']
        if 'age' in student_data:
            self.students_df.at[index, 'Age'] = int(student_data['age'])
        if 'absences' in student_data:
            self.students_df.at[index, 'Number_of_Absences'] = int(student_data['absences'])
        if 'internet_access' in student_data:
            self.students_df.at[index, 'Internet_Access'] = str(student_data['internet_access']).lower()
        if 'aggregate_grade' in student_data:
            try:
                agg = float(student_data['aggregate_grade'])
                self.students_df.at[index, 'Aggregate_Grade'] = agg
                self.students_df.at[index, 'Grade_1'] = agg
                self.students_df.at[index, 'Grade_2'] = agg
                self.students_df.at[index, 'Final_Grade'] = agg
            except (ValueError, TypeError):
                pass

        # Recompute risk if desired zone provided; else keep existing Risk_Category
        desired = str(student_data.get('desired_risk_zone') or '').strip()
        if desired in ['Red', 'Yellow', 'Green']:
            self.students_df.at[index, 'Risk_Category'] = desired

        # Refresh dashboard data
        self.dashboard_data = self.students_df.copy()
        if 'Dropped_Out' in self.dashboard_data.columns:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes'
            ).astype(int)
        else:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Risk_Category'].astype(str).str.strip().str.lower() == 'red'
            ).astype(int)

        self.write_students_json(self.students_df)

    def delete_student(self, index: int = None, name: str = None) -> str:
        """Delete a student by index or by name (first match)."""
        deleted_label = None
        
        if index is not None:
            if index < 0 or index >= len(self.students_df):
                raise ValueError('Index out of range')
            deleted_label = str(self.students_df.iloc[index].get('Name', f'Index {index}'))
            self.students_df = self.students_df.drop(self.students_df.index[index]).reset_index(drop=True)
        elif name:
            mask = self.students_df['Name'].astype(str).str.strip().str.lower() == name.lower()
            matches = self.students_df[mask]
            if matches.empty:
                raise ValueError('No student found with that name')
            first_idx = matches.index[0]
            deleted_label = str(self.students_df.loc[first_idx].get('Name', ''))
            self.students_df = self.students_df.drop(first_idx).reset_index(drop=True)
        else:
            raise ValueError('Provide index or name')

        # Recompute dashboard and rewrite JSON
        self.dashboard_data = self.students_df.copy()
        if 'Dropped_Out' in self.dashboard_data.columns:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes'
            ).astype(int)
        else:
            self.dashboard_data['DropoutFlag'] = (
                self.dashboard_data['Risk_Category'].astype(str).str.strip().str.lower() == 'red'
            ).astype(int)

        self.write_students_json(self.students_df)
        return deleted_label

    def get_students_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the latest N students with names and risk info (tail)."""
        df = self.students_df.tail(limit).copy()
        # Sort by Risk_Category: Red (0), Yellow (1), Green (2), others (3)
        def _rank(val):
            v = str(val).strip().lower()
            if v == 'red':
                return 0
            if v == 'yellow':
                return 1
            if v == 'green':
                return 2
            return 3
        if 'Risk_Category' in df.columns:
            df['__risk_order'] = df['Risk_Category'].apply(_rank)
            df = df.sort_values(['__risk_order'], kind='stable').drop(columns=['__risk_order'])
        # Include original global index for stable editing
        df['_idx'] = df.index.astype(int)
        return json.loads(df.to_json(orient='records'))

    def get_risk_summary(self) -> Dict[str, int]:
        """Return counts for red/yellow/green and total students."""
        if 'Risk_Category' in self.students_df.columns:
            cats = self.students_df['Risk_Category'].astype(str).str.strip().str.lower()
            red = int((cats == 'red').sum())
            yellow = int((cats == 'yellow').sum())
            green = int((cats == 'green').sum())
        else:
            # Fallback using DropoutFlag if Risk_Category not present
            flags = self.dashboard_data['DropoutFlag'] if 'DropoutFlag' in self.dashboard_data.columns else pd.Series([0]*len(self.students_df))
            red = int(flags.sum())
            yellow = 0
            green = int(len(self.students_df) - red)
        total = int(len(self.students_df))
        return {'total': total, 'red': red, 'yellow': yellow, 'green': green}

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data required for dashboard charts."""
        # 1. Dropout by Gender (using DropoutFlag)
        gender_col = 'Gender' if 'Gender' in self.dashboard_data.columns else None
        absences_col = 'Number_of_Absences' if 'Number_of_Absences' in self.dashboard_data.columns else None

        if gender_col is not None:
            gender_dropout = self.dashboard_data.groupby(gender_col)['DropoutFlag'].agg(['mean', 'count']).reset_index()
            gender_dropout['Dropout_Rate'] = round(gender_dropout['mean'] * 100, 1)
            gender_records = gender_dropout.rename(columns={gender_col: 'Gender'})[['Gender', 'Dropout_Rate']].to_dict('records')
        else:
            gender_records = []

        # 2. Dropout by Absences Bins
        if absences_col is not None:
            self.dashboard_data['Absence_Level'] = pd.cut(
                self.dashboard_data[absences_col],
                bins=[-0.1, 10, 20, 1000],
                include_lowest=True,
                right=False,
                labels=['Low', 'Medium', 'High']
            )
            absences_dropout = (
                self.dashboard_data
                .groupby('Absence_Level', observed=True)['DropoutFlag']
                .mean()
                .reset_index()
            )
            absences_dropout['Dropout_Rate'] = round(absences_dropout['DropoutFlag'] * 100, 1)
            absences_records = absences_dropout[['Absence_Level', 'Dropout_Rate']].to_dict('records')
        else:
            absences_records = []

        return {
            'gender_data': json.loads(json.dumps(gender_records)),
            'absences_data': json.loads(json.dumps(absences_records))
        }
