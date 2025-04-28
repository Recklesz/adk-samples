# FOMC Research Runner

This script runs the FOMC research agent with a specific query for the company "elevenlabs.io".

## Setup

1. Make sure you have set up the FOMC research agent according to its README in `agents/fomc-research/`.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Script

```bash
python run_fomc_research.py
```

This will:
1. Initialize the FOMC research agent
2. Send an initial greeting message
3. Query the agent with "elevenlabs.io" as the target company
4. Print the agent's responses

## Environment Variables

The script relies on the environment variables configured for the FOMC research agent. Ensure those are properly set before running. 