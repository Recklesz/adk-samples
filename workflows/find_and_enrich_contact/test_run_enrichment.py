import pandas as pd
import pytest
from unittest.mock import patch
from pathlib import Path
import sys
import importlib

# Import the enrichment script as a module
def import_enrichment_module(tmp_path):
    sys.path.insert(0, str(tmp_path))
    module = importlib.import_module("run_enrichment")
    sys.path.pop(0)
    return module

@pytest.fixture
def sample_input_csv(tmp_path):
    csv_path = tmp_path / "companies_data_1.csv"
    csv_path.write_text(
        "Company,Company Description,Number of Employees,Company Domain (website url)\n"
        "Fundraise Up,desc,182-260,fundraiseup.com\n"
        "Jobgether,desc,11-50,jobgether.com\n"
    )
    return csv_path

@pytest.fixture
def expected_contacts():
    return {
        'fundraiseup.com': {
            'contact_name': 'Carolina Khan',
            'contact_email': 'carolina@fundraiseup.com',
            'contact_title': 'Head of Partnerships',
            'linkedin_url': 'http://linkedin.com/in/carolina-khan'
        },
        'jobgether.com': {
            'contact_name': 'Alex Smith',
            'contact_email': 'alex@jobgether.com',  
            'contact_title': 'CEO',
            'linkedin_url': 'http://linkedin.com/in/alex-smith'
        }
    }

def fake_enrich_company(domain):
    # Simulate what the agent would return (like writing to contacts.csv)
    contacts = {
        'fundraiseup.com': {
            'contact_name': 'Carolina Khan',
            'contact_email': 'carolina@fundraiseup.com',
            'contact_title': 'Head of Partnerships',
            'linkedin_url': 'http://linkedin.com/in/carolina-khan'
        },
        'jobgether.com': {
            'contact_name': 'Alex Smith',
            'contact_email': 'alex@jobgether.com',
            'contact_title': 'CEO',
            'linkedin_url': 'http://linkedin.com/in/alex-smith'
        }
    }
    return contacts.get(domain, {})

def test_enrichment_pipeline(sample_input_csv, tmp_path, expected_contacts):
    output_csv = tmp_path / "companies_data_1_enriched.csv"
    # Patch enrich_company to simulate agent output
    import run_enrichment
    with patch.object(run_enrichment, 'enrich_company', side_effect=fake_enrich_company):
        run_enrichment.main(str(sample_input_csv), str(output_csv), concurrency=2)
    df = pd.read_csv(output_csv)
    for domain, expected in expected_contacts.items():
        row = df[df['Company Domain (website url)'] == domain].iloc[0]
        assert row['contact_name'] == expected['contact_name']
        assert row['contact_email'] == expected['contact_email']
        assert row['contact_title'] == expected['contact_title']
        assert row['linkedin_url'] == expected['linkedin_url']
