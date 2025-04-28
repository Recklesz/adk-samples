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

"""'save_contact_to_csv' tool for storing final contact information"""

import csv
import logging
import os
from typing import Dict, Any, Optional

from google.adk.tools import ToolContext
from google.genai.types import Part

logger = logging.getLogger(__name__)


def save_contact_to_csv_tool(
    first_name: str, 
    last_name: str, 
    company_name: str, 
    tool_context: ToolContext,
    linkedin_url: Optional[str] = None, 
    email: Optional[str] = None
) -> Dict[str, Any]:
    """Saves contact information to a CSV file.

    Args:
      first_name: First name of the contact
      last_name: Last name of the contact
      company_name: Company name
      tool_context: ToolContext object
      linkedin_url: LinkedIn profile URL (optional)
      email: Email address (optional)

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    logger.info(
        "Saving contact: %s %s from %s to CSV",
        first_name,
        last_name,
        company_name
    )
    
    # Create a contacts data folder if it doesn't exist
    data_folder = "contact_data"
    os.makedirs(data_folder, exist_ok=True)
    
    # File path for the CSV
    csv_file = os.path.join(data_folder, "contacts.csv")
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_file)
    
    # Prepare contact data
    contact_data = {
        "First Name": first_name,
        "Last Name": last_name,
        "Company Name": company_name,
        "LinkedIn URL": linkedin_url or "",
        "Email": email or ""
    }
    
    # Write to CSV file
    try:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ["First Name", "Last Name", "Company Name", "LinkedIn URL", "Email"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header if file is being created for the first time
            if not file_exists:
                writer.writeheader()
            
            # Write the contact data
            writer.writerow(contact_data)
        
        # Also store the contact info in state for later use
        tool_context.state.update({
            "last_saved_contact": contact_data
        })
        
        # Create a readable summary for the user
        summary = (
            f"Contact saved: {first_name} {last_name} from {company_name}\n"
            f"LinkedIn: {linkedin_url or 'Not provided'}\n"
            f"Email: {email or 'Not provided'}"
        )
        
        # Save summary as an artifact
        tool_context.save_artifact(
            filename="contact_summary",
            artifact=Part(text=summary)
        )
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error("Error saving contact to CSV: %s", e)
        return {
            "status": "error",
            "error_message": f"Failed to save contact to CSV: {str(e)}"
        } 