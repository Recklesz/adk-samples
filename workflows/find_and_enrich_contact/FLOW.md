# Enrichment Pipeline: Intended Flow

## 1. Input
- You start with a list of companies (usually in a CSV or database), each identified by its domain.

## 2. Concurrency Limit
- You define a maximum number of enrichment agents (workers) that can run at the same time. This is your "concurrency" setting.

## 3. Processing Loop
- The pipeline keeps track of which companies still need to be enriched.
- At any given moment, up to N agents (where N = concurrency limit) are running in parallel.

## 4. Agent Lifecycle
For each company to be processed:
- A new agent is launched. This agent is a fresh, isolated process.
- The agent receives the company domain and does all the research/enrichment work for that one company.
- When the agent finishes (success or failure), it is completely shut down and cleaned up.
- If there are more companies to process, a new agent is launched for the next one, keeping the number of simultaneous agents at or below the concurrency limit.

## 5. Data Collection
- Each agent saves the result of its enrichment (e.g., contact info, notes, errors) in a structured format.
- The main pipeline collects these results as agents finish.

## 6. Output
- Once all companies have been processed, the pipeline merges all the results into a final output file (e.g., an enriched CSV).

## 7. Cleanup
- Any temporary files, logs, or resources used by the agents are cleaned up as each agent finishes.

## Key Points
- **One agent = one company = one process**: Each company is handled by a brand new, short-lived agent process.
- **No agent is reused**: After finishing, the agent is gone.
- **Concurrency controls how many agents are running at the same time**: If set to 2, there are never more than 2 agents working at once, but as soon as one finishes, a new one can start.
- **Isolation**: Each agent is fully isolated from the others, so bugs or crashes in one don't affect the rest.