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

import pytest
from google.adk.tools import ToolContext

from fomc_research.tools.query_lemlist import query_lemlist_tool


class TestQueryLemlistTool(unittest.TestCase):
    """Tests for the query_lemlist_tool function."""

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

    @mock.patch("fomc_research.tools.query_lemlist.requests.get")
    def test_successful_api_call(self, mock_get):
        """Test a successful API call with valid parameters."""
        # Set up mock response
        mock_response = mock.MagicMock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "companyName": "Example Corp",
            }
        ]
        mock_get.return_value = mock_response
        
        # Set up tool context state
        self.tool_context.state = {"company_name": "Example Corp"}
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result == {"status": "ok"}
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once_with(
            "https://api.lemlist.com/api/people",
            auth=("", "test_api_key"),
            params={"companyName": "Example Corp", "limit": 20, "page": 1},
            timeout=10,
        )
        
        # Verify state was updated
        assert "lemlist_people" in self.tool_context.state
        assert self.tool_context.state["lemlist_people"] == mock_response.json.return_value

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

    @mock.patch("fomc_research.tools.query_lemlist.requests.get")
    def test_api_request_exception(self, mock_get):
        """Test behavior when API request raises an exception."""
        # Set up mock to raise an exception
        mock_get.side_effect = Exception("API connection error")
        
        # Set up tool context state
        self.tool_context.state = {"company_name": "Example Corp"}
        
        # Call the function
        result = query_lemlist_tool(self.tool_context)
        
        # Verify the result
        assert result["status"] == "error"
        assert "API connection error" in result["error_message"]
        
        # Verify state was not updated
        assert "lemlist_people" not in self.tool_context.state

    @mock.patch("fomc_research.tools.query_lemlist.requests.get")
    def test_custom_limit_and_page(self, mock_get):
        """Test API call with custom limit and page parameters."""
        # Set up mock response
        mock_response = mock.MagicMock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "companyName": "Example Corp",
            }
        ]
        mock_get.return_value = mock_response
        
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
        mock_get.assert_called_once_with(
            "https://api.lemlist.com/api/people",
            auth=("", "test_api_key"),
            params={"companyName": "Example Corp", "limit": 50, "page": 2},
            timeout=10,
        )
        
        # Verify state was updated
        assert "lemlist_people" in self.tool_context.state
