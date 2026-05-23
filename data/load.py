import pandas as pd
from pathlib import Path

# dictionary key conversion
COLUMN_MAP = {
    'Region': 'region',
    'Division': 'division',
    'District': 'district',
    'BEIS School ID': 'school_id',
    'School Name': 'name',
    'Street Address': 'address',
    'Municipality': 'municipality',
    'Legislative District': 'legislative_district',
    'Barangay': 'barangay',
    'Sector': 'sector',
    'Urban/Rural': 'urban_rural',
    'School Subclassification': 'subclass',
    'Modified Curricural Offering Classification': 'offering',
}

CATEGORICAL_COLS = [
    'region', 'division', 'district', 'municipality', 'legislative_district',
    'barangay', 'sector', 'urban_rural', 'subclass', 'offering',
]

def load_schools(csv_path: str) -> pd.DataFrame:
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path, dtype={'BEIS School ID': str})
    if set(df.columns) != set(COLUMN_MAP.keys()):
        raise ValueError(f"Unexpected columns in {csv_path}: {df.columns.tolist()}")
    df = df.rename(columns=COLUMN_MAP)
    df[CATEGORICAL_COLS] = df[CATEGORICAL_COLS].astype('category')
    return df


