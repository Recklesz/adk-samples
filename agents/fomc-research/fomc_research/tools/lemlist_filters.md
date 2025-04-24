Available filters: [
{
"filterId": "leadsByIds",
"description": "Leads by \_id",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "companiesByIds",
"description": "Companies by \_id",
"mode": [
"companies"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "currentTitle",
"description": "Current job title",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentTitleWithExactMatch",
"description": "Current job title",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "country",
"description": "Country",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "region",
"description": "Region",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Europe",
"Western Europe",
"Southern Europe",
"Northern Europe",
"Eastern Europe",
"Balkans",
"DACH",
"America",
"North America",
"Central America",
"Caribbean",
"South America",
"Africa",
"North Africa (Maghreb)",
"West Africa",
"Central Africa",
"East Africa",
"Southern Africa",
"Asia",
"East Asia",
"Southeast Asia",
"South Asia",
"Central Asia",
"Middle East",
"Oceania"
]
},
{
"filterId": "keyword",
"description": "Keyword in profile",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "department",
"description": "Department",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Accounting",
"Administrative",
"Arts and Design",
"Business Development",
"Community and Social Services",
"Consulting",
"Education",
"Engineering",
"Entrepreneurship",
"Finance",
"Healthcare Services",
"Human Resources",
"Information Technology",
"Legal",
"Marketing",
"Media and Communication",
"Military and Protective Services",
"Operations",
"Other",
"Product Management",
"Program and Project Management",
"Purchasing",
"Quality Assurance",
"Real Estate",
"Research",
"Sales",
"Support"
]
},
{
"filterId": "currentPositionTenure",
"description": "Current position tenure",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Less than 6 months",
"6 months to 1 year",
"1 to 3 years",
"3 to 5 years",
"More than 5 years"
]
},
{
"filterId": "seniority",
"description": "Seniority",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Owner/Partner",
"CxO",
"Vice President",
"Director",
"Experienced Manager",
"Entry level Manager",
"Manager",
"Strategic",
"Senior",
"Entry level",
"in Training"
]
},
{
"filterId": "yearsOfExperience",
"description": "Years of experience",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"less than 1 year",
"1 to 2 years",
"2 to 5 years",
"5 to 10 years",
"More than 10 years"
]
},
{
"filterId": "numberOfConnections",
"description": "Number of connections",
"mode": [
"leads"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"less than 50",
"51-250",
"251-500",
"500+"
]
},
{
"filterId": "pastTitle",
"description": "Past job title",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanySizeGrowth",
"description": "Company size growth (3m.)",
"mode": [
"leads",
"companies"
],
"type": "slider",
"helper": "Use a min and max value (fill the in array once with a string formatted as 10|50). The min value is -100 and the max value is 200. Values are in percentage."
},
{
"filterId": "currentCompanyHiring",
"description": "Company is hiring",
"mode": [
"leads",
"companies"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanyTechnologies",
"description": "Company technologies",
"mode": [
"leads",
"companies"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanyLastFundingRoundAt",
"description": "Company last funding date",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Less than 1 month",
"1 month to 3 months",
"3 months to 6 months",
"More than 6 months"
]
},
{
"filterId": "currentCompanyRevenue",
"description": "Company revenue",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"$0 - $500K",
"$500K - $1M",
"$1M - $3M",
"$3M - $5M",
"$5M - $10M",
"$10M - $20M",
"$20M - $30M",
"$30M+"
]
},
{
"filterId": "keywordInCompany",
"description": "Keyword in company",
"mode": [
"leads",
"companies"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "currentCompanyHeadcount",
"description": "Company size",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"1-10",
"11-50",
"51-200",
"201-500",
"501-1000",
"1001-5000",
"5001-10000",
"10001+"
]
},
{
"filterId": "currentCompanyMarket",
"description": "Company market",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"B2C",
"B2B",
"B2B/B2C"
]
},
{
"filterId": "currentCompanyType",
"description": "Company type",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Public Company",
"Privately Held",
"Nonprofit",
"Educational Institution",
"Educational",
"Partnership",
"Self Employed",
"Self Owned",
"Government Agency",
"Sole Proprietorship"
]
},
{
"filterId": "currentCompany",
"description": "Company name",
"mode": [
"leads",
"companies"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanyByIds",
"description": "Current company by \_id",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "currentCompanyFounded",
"description": "Company founded year",
"mode": [
"leads",
"companies"
],
"type": "slider",
"helper": "Use a min and max value (fill the in array once with a string formatted as 1980|2010). The min value is 1900 and the max value is 2025."
},
{
"filterId": "currentCompanyCountry",
"description": "Company country",
"mode": [
"leads",
"companies"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanyRegion",
"description": "Company region",
"mode": [
"leads",
"companies"
],
"type": "select",
"helper": "Select a value from the associated list of values (to fill the in and/or out array)",
"values": [
"Europe",
"Western Europe",
"Southern Europe",
"Northern Europe",
"Eastern Europe",
"Balkans",
"DACH",
"America",
"North America",
"Central America",
"Caribbean",
"South America",
"Africa",
"North Africa (Maghreb)",
"West Africa",
"Central Africa",
"East Africa",
"Southern Africa",
"Asia",
"East Asia",
"Southeast Asia",
"South Asia",
"Central Asia",
"Middle East",
"Oceania"
]
},
{
"filterId": "currentCompanyLocation",
"description": "Company city / state",
"mode": [
"leads",
"companies"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "currentCompanyLinkedInUrl",
"description": "Company LinkedIn URL",
"mode": [
"leads",
"companies"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "currentCompanyWebsiteUrl",
"description": "Company Website URL",
"mode": [
"leads",
"companies"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "username",
"description": "Full Name",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "location",
"description": "City / State",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "interest",
"description": "Interests",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "numberOfLeadsPerCompany",
"description": "Number of leads per company",
"mode": [
"companies"
],
"type": "slider",
"helper": "Use a min and max value (fill the in array once with a string formatted as 1|200). The min value is 1 and the max value is 1000."
},
{
"filterId": "skill",
"description": "Skills",
"mode": [
"leads"
],
"type": "autocomplete",
"helper": ""
},
{
"filterId": "schoolName",
"description": "School name",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "schoolDegree",
"description": "School degree",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "leadLinkedInUrl",
"description": "Contact LinkedIn URL",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
},
{
"filterId": "leadLinkedInSlug",
"description": "Contact LinkedIn slug",
"mode": [
"leads"
],
"type": "text",
"helper": "Use free text search (to fill the in and/or out array)"
}
]
