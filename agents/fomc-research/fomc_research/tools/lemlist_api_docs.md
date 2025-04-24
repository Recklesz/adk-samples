# Lemlist API Documentation

## Overview
This document contains information about the Lemlist API integration for the CSV Spreadsheet Editor project. It records our findings from API testing and provides guidance for future development.

## API Endpoints

### People Database API
- **Endpoint**: `https://api.lemlist.com/api/database/people`
- **Method**: POST
- **Authentication**: Basic Auth with empty username and API key as password
- **Content-Type**: application/json

### Filters API
- **Endpoint**: `https://api.lemlist.com/api/database/filters`
- **Method**: GET
- **Authentication**: Basic Auth with empty username and API key as password

## Request Format

### People Search Request
```json
{
  "filters": [
    {
      "filterId": "currentCompany",
      "in": ["Company Name"],
      "out": []
    }
  ],
  "page": 1,
  "size": 20
}
```

## Important Findings

1. **Company Name Filter**: The correct filter ID for searching by company name is `currentCompany`, not `companyName`, `company`, or other variations.

2. **Empty Filters**: The API does not accept empty filters array and will return a 400 error.

3. **Schema Endpoint**: The `/api/database/people/schema` endpoint returns HTML instead of JSON, suggesting it may be a web interface rather than an API endpoint.

4. **Response Structure**: The response includes a `results` array containing contact objects with fields like:
   - `_id`
   - `full_name`
   - `lead_linkedin_url`
   - `current_exp_company_name`
   - `location`
   - And many others (see sample response below)

5. **Rate Limiting**: The API has rate limits as indicated by the `x-ratelimit-*` headers in the response.

## Sample Response Fields

Based on our API testing, here are the fields available in the contact objects:

- `_id`
- `_score`
- `canonical_shorthand_name`
- `connections_count`
- `connections_count_bucket`
- `country`
- `current_exp_company_industry`
- `current_exp_company_name`
- `current_exp_company_subindustry`
- `department`
- `education`
- `experience_count`
- `experiences`
- `full_name`
- `headline`
- `interests`
- `is_hidden`
- `languages`
- `lead_id`
- `lead_linkedin_url`
- `lead_logo_url`
- `lead_quality_score`
- `linkedin_short`
- `location`
- `skills`
- `summary`
- `updated_at`
- `years_of_exp_bucket`

## Error Handling

The API returns the following error codes:
- `400`: Bad Request - Usually indicates invalid filter ID or format
- `401`: Unauthorized - Invalid API key
- `403`: Forbidden - Insufficient permissions
- `429`: Too Many Requests - Rate limit exceeded

## Best Practices

1. Always use the `currentCompany` filter ID for company name searches.
2. Include proper error handling for API responses.
3. Respect rate limits by checking the `x-ratelimit-*` headers.
4. Store the API key securely in environment variables.
