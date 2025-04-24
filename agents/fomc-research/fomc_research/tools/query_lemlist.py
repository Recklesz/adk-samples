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

"""'query_lemlist' tool for FOMC Research sample agent."""

import logging
import os

import requests
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def query_lemlist_tool(tool_context: ToolContext) -> dict[str, str]:
    """Queries Lemlist People Database API for contacts by company name.

    Expected state keys:
      company_name: Name of the company to filter contacts.
      limit: (optional) number of results per page (default 20).
      page: (optional) page number to retrieve (default 1).

    Returns:
      A dict with "status" and optional "error_message" keys.
    """
    company_name = tool_context.state.get("company_name")
    if not company_name:
        logger.error("Missing company_name in state")
        return {"status": "error", "error_message": "Missing company_name in state"}

    limit = tool_context.state.get("limit", 20)
    page = tool_context.state.get("page", 1)

    api_key = os.getenv("LEMLIST_API_KEY")
    if not api_key:
        logger.error("Missing LEMLIST_API_KEY environment variable")
        return {"status": "error", "error_message": "Missing LEMLIST_API_KEY environment variable"}

    url = "https://api.lemlist.com/api/people"
    params = {
        "companyName": company_name,
        "limit": limit,
        "page": page,
    }

    logger.info(
        "Querying Lemlist People API for company: %s, limit: %s, page: %s",
        company_name, limit, page,
    )
    try:
        response = requests.get(url, auth=("", api_key), params=params, timeout=10)
        response.raise_for_status()
        contacts = response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error querying Lemlist API: %s", e)
        return {"status": "error", "error_message": f"Error querying Lemlist API: {e}"}

    tool_context.state.update({"lemlist_people": contacts})
    return {"status": "ok"}
