#!/usr/bin/env python
"""
Direct test script for the Lemlist API.
This script makes direct API calls to Lemlist to test different filter IDs and authentication methods.

Usage:
    python test_lemlist_api_direct.py
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def test_lemlist_api():
    """Test the Lemlist API directly with various configurations."""
    # Get API key from environment
    api_key = os.environ.get("LEMLIST_API_KEY")
    if not api_key:
        print("Error: LEMLIST_API_KEY not found in environment variables")
        return
    
    print(f"Using API key: {api_key[:5]}...{api_key[-3:]} (length: {len(api_key)})")
    
    # Test parameters
    company_website = "attio.com"  # Company website URL to search for
    position = "CEO"              # Position/title to search for
    
    # Common headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Step 1: Get available filters first
    print("\n=== STEP 1: Getting available filters ===\n")
    filters_url = "https://api.lemlist.com/api/database/filters"
    
    try:
        print(f"Making GET request to: {filters_url}")
        filters_response = requests.get(
            filters_url,
            headers=headers,
            auth=("", api_key),
            timeout=10
        )
        
        print(f"Response status code: {filters_response.status_code}")
        print(f"Response headers: {dict(filters_response.headers)}")
        
        if filters_response.status_code == 200:
            try:
                filters_data = filters_response.json()
                print(f"Available filters: {json.dumps(filters_data, indent=2)}")
                
                # Extract valid filter IDs
                valid_filter_ids = []
                if isinstance(filters_data, list):
                    for filter_item in filters_data:
                        if isinstance(filter_item, dict) and 'id' in filter_item:
                            valid_filter_ids.append(filter_item['id'])
                            print(f"Found filter ID: {filter_item['id']} - {filter_item.get('label', 'No label')}")
                
                if valid_filter_ids:
                    print(f"\nValid filter IDs: {valid_filter_ids}")
                else:
                    print("No valid filter IDs found in response")
                    # Fall back to our guesses
                    valid_filter_ids = ["companyName", "company", "organization", "org"]
            except ValueError:
                print(f"Response is not JSON. Content: {filters_response.text[:500]}...")
                # Fall back to our guesses
                valid_filter_ids = ["companyName", "company", "organization", "org"]
        else:
            print(f"Failed to get filters. Response: {filters_response.text[:500]}...")
            # Fall back to our guesses
            valid_filter_ids = ["companyName", "company", "organization", "org"]
    except requests.exceptions.RequestException as e:
        print(f"Request error getting filters: {e}")
        # Fall back to our guesses
        valid_filter_ids = ["companyName", "company", "organization", "org"]
    
    # Step 2: Try searching with the correct filter ID
    print("\n=== STEP 2: Searching with the correct filter ID ===\n")
    
    # API endpoint for people search
    url = "https://api.lemlist.com/api/database/people"
    
    # Based on our API testing, we need to use multiple filters:
    # - "currentCompanyWebsiteUrl" for company website URL
    # - "currentTitle" for job title/position
    print(f"\n--- Testing with multiple filters (company website: {company_website}, position: {position}) ---")
    
    # Request body with multiple filters
    request_body = {
        "filters": [
            {
                "filterId": "currentCompanyWebsiteUrl",
                "in": [company_website],
                "out": []
            },
            {
                "filterId": "currentTitle",
                "in": [position],
                "out": []
            }
        ],
        "page": 1,
        "size": 20
    }
        
    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request body: {json.dumps(request_body, indent=2)}")
        
    try:
        # Make the API call with Basic Auth (empty username, API key as password)
        response = requests.post(
            url, 
            headers=headers, 
            json=request_body,
            auth=("", api_key),
            timeout=10
        )
            
        # Print response details
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
            
        # Try to parse the response as JSON
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)[:500]}...")
                
            # If successful, print more details
            if response.status_code == 200:
                if isinstance(response_json, dict) and 'results' in response_json:
                    results = response_json['results']
                    print(f"Found {len(results)} contacts")
                    
                    if results:
                        print("\nSample contact:")
                        sample = results[0]
                        for key in sorted(sample.keys()):
                            print(f"  {key}: {sample.get(key)}")
                        
                        print("\nAvailable fields:")
                        for key in sorted(sample.keys()):
                            print(f"  {key}")
                else:
                    print(f"Unexpected response format: {type(response_json)}")
        except ValueError:
            print(f"Response is not JSON. Content: {response.text[:500]}...")
                
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    
    print(f"--- End of test with multiple filters ---\n")
    
    # Step 3: Try with a simpler request format (just website URL)
    print("\n=== STEP 3: Testing with just website URL filter ===\n")
    
    # Making request with only the website URL filter
    print(f"Making request with only website URL filter: {company_website}")
    request_body = {
        "filters": [
            {
                "filterId": "currentCompanyWebsiteUrl",
                "in": [company_website],
                "out": []
            }
        ],
        "page": 1,
        "size": 20
    }
    
    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request body: {json.dumps(request_body, indent=2)}")
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=request_body,
            auth=("", api_key),
            timeout=10
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)[:500]}...")
        except ValueError:
            print(f"Response is not JSON. Content: {response.text[:500]}...")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        
    # Step 4: Try getting the people schema
    print("\n=== STEP 4: Getting people schema ===\n")
    
    schema_url = "https://api.lemlist.com/api/database/people/schema"
    
    try:
        print(f"Making GET request to: {schema_url}")
        schema_response = requests.get(
            schema_url,
            headers=headers,
            auth=("", api_key),
            timeout=10
        )
        
        print(f"Response status code: {schema_response.status_code}")
        
        try:
            schema_data = schema_response.json()
            print(f"People schema: {json.dumps(schema_data, indent=2)[:500]}...")
        except ValueError:
            print(f"Response is not JSON. Content: {schema_response.text[:500]}...")
    except requests.exceptions.RequestException as e:
        print(f"Request error getting schema: {e}")

if __name__ == "__main__":
    test_lemlist_api()
