import pytest
import pandas as pd
from process_csv import load_schools

HEADER = "Region,Division,District,BEIS School ID,School Name,Street Address,Municipality,Legislative District,Barangay,Sector,Urban/Rural,School Subclassification,Modified Curricural Offering Classification"
ROW = "VIII,Leyte,District 1,000251,Sample Elementary,Brgy. A,Tacloban,1st,Brgy. A,Public,Urban,Regular,Elementary"

def test_load_schools_returns_dataframe(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(f"{HEADER}\n{ROW}\n")
    result = load_schools(str(csv_file))
    assert isinstance(result, pd.DataFrame)

def test_load_schools_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_schools(str(tmp_path / "nonexistent.csv"))

def test_load_schools_school_id_preserved_as_string(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(f"{HEADER}\n{ROW}\n")
    result = load_schools(str(csv_file))
    assert result['BEIS School ID'].dtype == object
    assert result['BEIS School ID'].iloc[0] == '000251'
