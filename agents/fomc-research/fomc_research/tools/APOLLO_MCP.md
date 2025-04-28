### Available Tools

The server exposes the following powerful Apollo.io integration tools:

1. **people_enrichment**
   - Use the People Enrichment endpoint to enrich data for 1 person
   - Parameters:
     - `first_name` (string, optional): Person's first name
     - `last_name` (string, optional): Person's last name
     - `email` (string, optional): Person's email address
     - `domain` (string, optional): Company domain
     - `organization_name` (string, optional): Organization name
   - Example:
     ```json
     {
       "first_name": "John",
       "last_name": "Doe",
       "email": "john.doe@example.com"
     }
     ```

2. **organization_enrichment**
   - Use the Organization Enrichment endpoint to enrich data for 1 company
   - Parameters:
     - `domain` (string, optional): Company domain
     - `name` (string, optional): Company name
   - Example:
     ```json
     {
       "domain": "apollo.io"
     }
     ```

3. **people_search**
   - Use the People Search endpoint to find people
   - Parameters:
     - `q_organization_domains_list` (array, optional): List of organization domains to search within
     - `person_titles` (array, optional): List of job titles to search for
     - `person_seniorities` (array, optional): List of seniority levels to search for
   - Example:
     ```json
     {
       "person_titles": ["Marketing Manager"],
       "person_seniorities": ["vp"],
       "q_organization_domains_list": ["apollo.io"]
     }
     ```

4. **organization_search**
   - Use the Organization Search endpoint to find organizations
   - Parameters:
     - `q_organization_domains_list` (array, optional): List of organization domains to search for
     - `organization_locations` (array, optional): List of organization locations to search for
   - Example:
     ```json
     {
       "organization_locations": ["Japan", "Ireland"]
     }
     ```

5. **organization_job_postings**
   - Use the Organization Job Postings endpoint to find job postings for a specific organization
   - Parameters:
     - `organization_id` (string, required): Apollo.io organization ID
   - Example:
     ```json
     {
       "organization_id": "5e60b6381c85b4008c83"
     }
     ```
