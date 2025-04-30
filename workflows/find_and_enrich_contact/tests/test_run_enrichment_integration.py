import pandas as pd
from pathlib import Path
from unittest.mock import patch
import sys
import pytest

# Ensure the parent directory (where run_enrichment.py lives) is in sys.path
PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

import run_enrichment

def test_single_row_enrichment_integration(tmp_path):
    # Locate the input CSV with 1 entry
    input_csv = Path(__file__).parent / "test_data" / "companies_data_1_entry.csv"
    output_csv = tmp_path / "companies_data_1_entry_enriched.csv"

    # Run the real enrichment pipeline (no patching)
    run_enrichment.main(str(input_csv), str(output_csv), concurrency=1)

    # Debug: List files in the temp output directory
    print(f"Temp output directory contents: {[str(p) for p in tmp_path.iterdir()]}")
    # Assert output file exists
    assert output_csv.exists(), f"Expected output file {output_csv} was not created"

    import pandas as pd
    df = pd.read_csv(output_csv)
    print('Output CSV contents:')
    print(df)
    print('Output CSV columns:')
    print(df.columns)
    # Find the enriched row for fundraiseup.com
    row = df[df['Company Domain (website url)'] == 'fundraiseup.com'].iloc[0]
    # Check that enrichment columns exist and are not empty
    for col in ['First Name', 'Last Name', 'Email', 'LinkedIn URL']:
        assert col in row, f"Column {col} missing from output"
        assert isinstance(row[col], str) and row[col].strip() != "", f"Column {col} is empty"
    # Optionally print the enriched row for debugging
    print(row)
