import pandas as pd
from pathlib import Path

COLUMNS = [
    'BEIS School ID', 'School Name', 'Street Address'
]

CATEGORICAL_COLUMNS = [
    'Region', 'Division', 'District', 'Municipality', 'Legislative District',
    'Barangay', 'Sector', 'Urban/Rural', 'School Subclassification',
    'Modified Curricural Offering Classification',
]

def load_schools(csv_path: str) -> pd.DataFrame:
    """Load masterlist of all schools in PH 2020-2021 from csv file"""
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path, dtype={'BEIS School ID': str}) # parses school id as string
    if df.columns.tolist() != CATEGORICAL_COLUMNS[:3] + COLUMNS + CATEGORICAL_COLUMNS[3:]:
        raise ValueError(f"Unexpected columns in {csv_path}: {df.columns.tolist()}")
    df[CATEGORICAL_COLUMNS] = df[CATEGORICAL_COLUMNS].astype('category')
    return df

DF = load_schools('data/beis_project.csv')