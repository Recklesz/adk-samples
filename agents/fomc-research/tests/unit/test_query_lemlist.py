# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the query_lemlist tool."""

import os
import unittest
from unittest import mock
import json
from pathlib import Path

import pytest
import requests
from google.adk.tools import ToolContext
from dotenv import load_dotenv

from fomc_research.tools.query_lemlist import query_lemlist_tool

# Load environment variables from .env file
env_path = Path(__file__).parents[3] / ".env"
load_dotenv(dotenv_path=env_path)


class TestQueryLemlistTool(unittest.TestCase):
    """Tests for the query_lemlist_tool function.
    
    Includes both mock tests and a real API test using the actual API key.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock ToolContext with a state dictionary
        self.tool_context = mock.MagicMock(spec=ToolContext)
        self.tool_context.state = {}
        
        # Save original environment variable
        self.original_api_key = os.environ.get("LEMLIST_API_KEY")
        # Set a test API key
        os.environ["LEMLIST_API_KEY"] = "test_api_key"
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original environment variable
        if self.original_api_key:
            os.environ["LEMLIST_API_KEY"] = self.original_api_key
        else:
            os.environ.pop("LEMLIST_API_KEY", None)

    @mock.patch("fomc_research.tools.query_lemlist.requests.post")
    def test_successful_api_call(self, mock_post):
        """Test a successful API call with valid parameters.
        
        Tests both a simple company name filter and a multi-filter query with position.
        """
        # Set up mock response with a more comprehensive example of Lemlist API data
        mock_response = mock.MagicMock()
        expected_people = [
            {
                "id": "1",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "companyName": "Example Corp",
                "position": "CEO",
                "phone": "+1234567890",
                "linkedinUrl": "https://linkedin.com/in/johndoe",
                "status": "active"
            },
            {
                "id": "2",
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "companyName": "Example Corp",
                "position": "CTO",
                "phone": "+1987654321",
                "linkedinUrl": "https://linkedin.com/in/janesmith",
                "status": "active"
            }
        ]
        # Create a response format that matches the Lemlist API documentation
        expected_data = {
            "results": expected_people,
            "total": 2,
            "took": 42,
            "page": 1,
            "size": 20,
            "search": "abc123",
            "limitations": 100,
            "team": "team123"
        }
        mock_response.json.return_value = expected_data
        mock_post.return_value = mock_response
        
        # Set up tool context state
        self.tool_context.state = {"company_name": "Example Corp"}
        
        # Call the function for company name only
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "ok"}, f"Expected status 'ok', got {result}"
        
        # Verify the API was called with correct parameters (company name only)
        mock_post.assert_called_with(
            "https://api.lemlist.com/api/database/people",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "filters": [
                    {
                        "filterId": "currentCompany",
                        "in": ["Example Corp"],
                        "out": []
                    }
                ],
                "page": 1,
                "size": 20
            },
            auth=("", "test_api_key"),
            timeout=10,
        )
        
        # Reset the mock
        mock_post.reset_mock()
        
        # Now test with both company name and position
        self.tool_context.state = {
            "company_name": "Example Corp",
            "position": "CEO"
        }
        
        # Set up mock response again
        mock_post.return_value = mock_response
        
        # Call the function with position filter
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "ok"}, f"Expected status 'ok', got {result}"
        
        # Verify the API was called with both filters
        mock_post.assert_called_once_with(
            "https://api.lemlist.com/api/database/people",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "filters": [
                    {
                        "filterId": "currentCompany",
                        "in": ["Example Corp"],
                        "out": []
                    },
                    {
                        "filterId": "currentTitle",
                        "in": ["CEO"],
                        "out": []
                    }
                ],
                "page": 1,
                "size": 20
            },
            auth=("", "test_api_key"),
            timeout=10,
        )
        
        # Verify state was updated with the correct data
        assert "lemlist_people" in self.tool_context.state, "lemlist_people key not found in state"
        assert self.tool_context.state["lemlist_people"] == expected_data["results"], "State data doesn't match expected data"
        
        # Verify we can access specific fields in the data
        people_data = self.tool_context.state["lemlist_people"]
        assert len(people_data) == 2, f"Expected 2 people in data, got {len(people_data)}"
        assert people_data[0]["firstName"] == "John", f"Expected firstName 'John', got {people_data[0]['firstName']}"
        assert people_data[1]["position"] == "CTO", f"Expected position 'CTO', got {people_data[1]['position']}"

    def test_missing_company_name(self):
        """Test behavior when company_name is missing from state."""
        # Set up tool context state without company_name
        self.tool_context.state = {}
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "error", "error_message": "Missing company_name in state"}
        
        # Verify state was not updated
        assert "lemlist_people" not in self.tool_context.state

    def test_missing_api_key(self):
        """Test behavior when LEMLIST_API_KEY is missing."""
        # Remove API key from environment
        os.environ.pop("LEMLIST_API_KEY", None)
        
        # Set up tool context state
        self.tool_context.state = {"company_name": "Example Corp"}
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "error", "error_message": "Missing LEMLIST_API_KEY environment variable"}
        
        # Verify state was not updated
        assert "lemlist_people" not in self.tool_context.state

    @mock.patch("fomc_research.tools.query_lemlist.requests.post")
    def test_api_request_exception(self, mock_post):
        """Test behavior when API request raises an exception."""
        # Set up mock to raise an exception
        mock_post.side_effect = Exception("API connection error")
        
        # Set up tool context state
        self.tool_context.state = {"company_name": "Example Corp"}
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result["status"] == "error"
        assert "API connection error" in result["error_message"]
        
        # Verify state was not updated
        assert "lemlist_people" not in self.tool_context.state

    @mock.patch("fomc_research.tools.query_lemlist.requests.post")
    def test_custom_limit_and_page(self, mock_post):
        """Test API call with custom limit and page parameters."""
        # Set up mock response
        mock_response = mock.MagicMock()
        expected_people = [
            {
                "id": "1",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "companyName": "Example Corp",
            }
        ]
        # Create a response format that matches the Lemlist API documentation
        mock_response.json.return_value = {
            "results": expected_people,
            "total": 1,
            "page": 2,
            "size": 50
        }
        mock_post.return_value = mock_response
        
        # Set up tool context state with custom limit and page
        self.tool_context.state = {
            "company_name": "Example Corp",
            "limit": 50,
            "page": 2,
        }
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "ok"}
        
        # Verify the API was called with correct parameters
        mock_post.assert_called_once_with(
            "https://api.lemlist.com/api/database/people",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "filters": [
                    {
                        "filterId": "currentCompany",
                        "in": ["Example Corp"],
                        "out": []
                    }
                ],
                "page": 2,
                "size": 50
            },
            auth=("", "test_api_key"),
            timeout=10,
        )
        
        # Verify state was updated
        assert "lemlist_people" in self.tool_context.state
        
    def test_real_api_call(self):
        """Test with the actual Lemlist API using the real API key.
        
        This test makes a real API call to Lemlist using the API key from the .env file.
        It will be skipped if the API key is not available or invalid.
        """
        # Make sure we're using the real API key from .env, not the test one
        # First, save the current environment variable
        original_api_key = os.environ.get("LEMLIST_API_KEY")
        
        try:
            # Load the API key directly from .env file to ensure we're using the correct one
            # The .env file is in the fomc-research directory
            env_path = Path(__file__).parents[2] / ".env"  # Go up 2 levels: unit -> tests -> fomc-research
            print(f"Looking for .env file at: {env_path}")
            if not env_path.exists():
                self.skipTest(f".env file not found at {env_path}")
                
            # Parse the .env file manually to get the API key
            api_key = None
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('LEMLIST_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip()
                        # Remove quotes if present
                        api_key = api_key.strip('"\'')
                        break
            
            if not api_key:
                self.skipTest("LEMLIST_API_KEY not found in .env file")
            
            # Set the environment variable to the API key from .env
            os.environ["LEMLIST_API_KEY"] = api_key
            
            # Reset the tool context state
            self.tool_context.state = {}
            
            # Use a real company name that might exist in the Lemlist database
            test_company = "Google"
            
            # Use the correct filter ID discovered through API testing
            # The correct filter ID for company name is "currentCompany"
            filter_id = "currentCompany"
            
            # Set up the state with the company name
            # We don't need to specify filter_id as the tool now defaults to "currentCompany"
            self.tool_context.state = {
                "company_name": test_company
            }
            
            print(f"\nMaking API call with the correct filter_id: {filter_id}")
            
            # Make the API call
            result = query_lemlist_tool(self.tool_context)
            
            # Print the result for debugging
            print(f"API call result: {result}")
            
            # If we get here and the last result was an error, skip the test
            if result["status"] == "error":
                # Print API key info for debugging (partial, for security)
                print(f"\nUsing API key from .env: {api_key[:5]}...{api_key[-3:]} (length: {len(api_key)})")
                print(f"Making real API call to Lemlist for company: {test_company}")
                
                # Check if we got an error after trying all filter IDs
                if result["status"] == "error":
                    # Print the error but don't fail the test if it's an API issue
                    print(f"WARNING: API call returned an error: {result['error_message']}")
                self.skipTest(f"Skipping due to API error: {result['error_message']}")
            
            # Verify we got a successful response
            self.assertEqual(result["status"], "ok", 
                            f"Expected status 'ok', got {result}")
            
            # Verify state was updated
            self.assertIn("lemlist_people", self.tool_context.state, 
                        "lemlist_people key not found in state")
            
            # Print information about the response for verification
            people = self.tool_context.state["lemlist_people"]
            print(f"Found {len(people)} contacts for company '{test_company}'")
            
            if people:
                # Print the first contact as a sample
                print("\nSample contact data:")
                sample = people[0]
                for key in ['id', 'firstName', 'lastName', 'email', 'companyName']:
                    if key in sample:
                        print(f"  {key}: {sample[key]}")
                
                # Print all available fields
                print("\nAll available fields in the response:")
                for key in sorted(sample.keys()):
                    print(f"  {key}")
        finally:
            # Restore the original API key environment variable
            if original_api_key:
                os.environ["LEMLIST_API_KEY"] = original_api_key
            else:
                os.environ.pop("LEMLIST_API_KEY", None)
