
"""'query_lemlist' tool for FOMC Research sample agent."""

import logging
import os
from typing import Optional, List

import requests
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def query_lemlist_tool(company_website: Optional[str] = None, title: Optional[List[str]] = None, page: Optional[int] = None, size: Optional[int] = None, tool_context: Optional[ToolContext] = None) -> dict:
    """Queries Lemlist People Database API for contacts using various filters.

    This tool uses the Lemlist People Database API to search for contacts using various filters.
    It searches for contacts at a specific company website with specific job titles.

    Args:
      company_website: Website URL of the company to filter contacts. If not provided, will use tool_context.state["company_website"].
      title: List of job titles/positions to filter contacts (e.g. ["VP Sales", "Vice President Sales"]). If not provided, will use tool_context.state["position"].
      page: Page number to retrieve (default 1).
      size: Number of results per page (default 20).
      tool_context: ToolContext object.

    Returns:
      A dict with "status" key and:
        - On success: "contacts" (list of contacts found) and "total" (total number of results) keys
        - On error: "error_message" key
      The tool_context.state will also be updated with a "lemlist_people" key
      containing the list of contacts found.
    """
    # Get parameters from direct args or tool_context
    if tool_context:
        company_website = company_website or tool_context.state.get("company_website")
        title = title or tool_context.state.get("position")
        page = page or tool_context.state.get("page", 1)
        size = size or tool_context.state.get("limit", 20)
    else:
        # Default values if no tool_context
        page = page or 1
        size = size or 20
    
    # Ensure we have company website
    if not company_website:
        logger.error("Missing company website parameter")
        return {
            "status": "error", 
            "error_message": "Missing company website parameter"
        }

    api_key = os.getenv("LEMLIST_API_KEY")
    if not api_key:
        logger.error("Missing LEMLIST_API_KEY environment variable")
        return {"status": "error", "error_message": "Missing LEMLIST_API_KEY environment variable"}

    # Define the correct API endpoint according to documentation
    url = "https://api.lemlist.com/api/database/people"
    
    # Set up headers for the request
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Set up the filters list
    filters = []
    
    # Add company website filter
    filters.append({
        "filterId": "currentCompanyWebsiteUrl",
        "in": [company_website],
        "out": []
    })
    logger.info("Added company website filter: %s", company_website)
    
    # Add position/title filter if provided
    if title:
        logger.info("Adding position filter with multiple titles: %s", title)
        filters.append({
            "filterId": "currentTitle",
            "in": title,
            "out": []
        })
    
    # Add any additional filters from state
    additional_filters = tool_context.state.get("additional_filters", [])
    if additional_filters:
        logger.info("Adding %d additional filters", len(additional_filters))
        filters.extend(additional_filters)
    
    # Create the request body
    request_body = {
        "filters": filters,
        "page": page,
        "size": size
    }

    logger.info(
        "Querying Lemlist People Database API for company: %s, size: %s, page: %s",
        company_website, size, page,
    )
    
    # Log the request details
    logger.info("Request URL: %s", url)
    logger.info("Request headers: %s", headers)
    logger.info("Request body: %s", request_body)
    
    try:
        response = requests.post(
            url,
            auth=("", api_key),  # Lemlist uses the API key as the password with empty username
            headers=headers,
            json=request_body,
            timeout=10
        )
        
        # Log response details
        logger.info("Response status code: %s", response.status_code)
        logger.info("Response headers: %s", dict(response.headers))
        
        # Check if we got a successful response
        response.raise_for_status()
        
        # Log the raw response content for debugging
        logger.info("Response content (first 200 chars): %s", response.text[:200])
        
        # Check if the response is valid JSON
        if not response.text.strip():
            logger.error("Empty response from Lemlist API")
            return {"status": "error", "error_message": "Empty response from Lemlist API"}
        
        # Parse the JSON response
        response_data = response.json()
        
        # According to docs, the response should have a 'results' field with the contacts
        if not isinstance(response_data, dict) or 'results' not in response_data:
            logger.error("Unexpected response format. Expected dict with 'results' field, got: %s", 
                       type(response_data))
            return {"status": "error", "error_message": "Unexpected response format from Lemlist API"}
        
        # Extract the contacts from the results field
        contacts = response_data['results']
        
        # Log information about the response
        logger.info("Received %d contacts from Lemlist API", len(contacts))
        logger.info("Total results: %s", response_data.get('total', 'unknown'))
        logger.info("Query took: %s ms", response_data.get('took', 'unknown'))
        
        # Log a sample of the first contact if available
        if contacts:
            sample_contact = contacts[0]
            # Based on our API test, we know the actual field names in the response
            # The fields may include: _id, full_name, lead_linkedin_url, current_exp_company_name, etc.
            logger.info("Sample contact data: %s", 
                        {k: sample_contact.get(k) for k in ['_id', 'full_name', 'lead_linkedin_url', 'current_exp_company_name', 'location'] 
                         if k in sample_contact})
            
            # Log the number of available fields for reference
            logger.info("Number of available fields in contact data: %d", len(sample_contact.keys()))
        else:
            logger.info("No contacts found for company website: %s", company_website)
    
        # Store the contacts in the tool context state
        tool_context.state.update({"lemlist_people": contacts})
        
        # Return success status along with the contacts and total
        result = {
            "status": "ok",
            "contacts": contacts,          # Surface data directly to the agent
            "total": response_data.get("total", 0)
        }
        return result
        
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error querying Lemlist API: %s", http_err)
        error_details = ""
        if hasattr(http_err, 'response') and http_err.response:
            status_code = http_err.response.status_code
            logger.error("Response status code: %s", status_code)
            logger.error("Response content: %s", http_err.response.text[:200])
            
            # Handle specific error codes
            if status_code == 400:
                error_message = "Bad Request: The request format is incorrect. "
                error_message += "This could be due to:"
                error_message += "\n1. Invalid filter ID (try using a different filter ID)"
                error_message += "\n2. Invalid authentication"
                error_message += "\n3. Missing required parameters"
                error_message += "\n\nPlease check the Lemlist API documentation for the correct filter IDs."
                
                # Try to parse the error response for more details
                try:
                    error_json = http_err.response.json()
                    if error_json and isinstance(error_json, dict):
                        error_message += f"\n\nAPI Error Details: {error_json}"
                except Exception:
                    pass
                    
                return {"status": "error", "error_message": error_message}
            elif status_code == 401:
                return {"status": "error", "error_message": "Authentication failed: Invalid API key or insufficient permissions."}
            elif status_code == 403:
                return {"status": "error", "error_message": "Forbidden: Your account doesn't have access to this resource."}
            elif status_code == 429:
                return {"status": "error", "error_message": "Rate limit exceeded: Too many requests. Please try again later."}
                
            error_details = f" Status: {status_code}, Content: {http_err.response.text[:100]}..."
        return {"status": "error", "error_message": f"HTTP error querying Lemlist API: {http_err}.{error_details}"}
        
    except ValueError as json_err:
        logger.error("Failed to parse JSON response: %s", json_err)
        logger.error("Raw response content: %s", response.text[:200])
        return {"status": "error", "error_message": f"Failed to parse JSON response: {json_err}. Raw response: {response.text[:100]}..."}
        
    except requests.exceptions.RequestException as req_err:
        logger.error("Request error querying Lemlist API: %s", req_err)
        return {"status": "error", "error_message": f"Request error querying Lemlist API: {req_err}"}
        
    except Exception as e:
        logger.error("Unexpected error querying Lemlist API: %s", e)
        return {"status": "error", "error_message": f"Unexpected error querying Lemlist API: {e}"}
