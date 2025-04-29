## Running the Script

```bash
poetry run python run_fomc_research.py
```

```bash
poetry run pytest test_run_enrichment.py
```

This will:

1. Initialize the FOMC research agent
2. Send an initial greeting message
3. Query the agent with "elevenlabs.io" as the target company
4. Print the agent's responses

## Environment Variables

The script relies on the environment variables configured for the FOMC research agent. Ensure those are properly set before running.
