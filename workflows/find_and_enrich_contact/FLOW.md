# Enrichment Pipeline: Refactored ADK Flow

## 1. Goal Definition
Transition the enrichment workflow from the previous custom concurrency model to utilize Google ADK's built-in dynamic parallel processing capabilities. The objective is to process a list of company domains from a CSV file, enrich each domain using the `fomc-research` agent, and output the results to a new CSV file, leveraging ADK's `ParallelAgent` for efficient, dynamically scaled execution.

## 2. Key Components
- **Input:** A CSV file containing company domains (e.g., `companies_data_1.csv`).
- **Processing Unit:** The `fomc-research` agent (`agents/fomc-research/fomc_research/agent.py`), responsible for researching and enriching data for a single domain.
- **Orchestration:** Google ADK agents.
- **Output:** An enriched CSV file containing the original domains and the data retrieved by the agents (e.g., `enriched_companies.csv`).

## 3. Proposed ADK Architecture
The workflow will be orchestrated by a root `SequentialAgent` containing the following sub-agents:

1.  **`CsvReaderAgent` (Custom `BaseAgent`):**
    *   Reads the input CSV file.
    *   Extracts the list of company domains.
    *   Places the list of domains into the shared `session.state` for the next agent.
    *   Generates a unique `run_id` for this execution batch.

2.  **`DynamicDispatcherAgent` (Custom `BaseAgent`):**
    *   Retrieves the list of domains and the `run_id` from `session.state`.
    *   For *each* domain in the list:
        *   Creates a *new instance* of the `fomc-research` agent, passing the domain and `run_id` (for state tracking).
    *   Dynamically constructs a `ParallelAgent` instance, providing the list of newly created `fomc-research` agent instances as its `sub_agents`.
    *   Executes this `ParallelAgent` using `parallel.run_async(ctx)`.
    *   Each `fomc-research` agent instance will run concurrently, performing its task and updating the shared `session.state` with its results, keyed uniquely (e.g., using `result:{run_id}:{domain}`).

3.  **`CsvWriterAgent` (Custom `BaseAgent`):**
    *   Retrieves the `run_id` from `session.state`.
    *   Collects all results associated with the current `run_id` from `session.state`.
    *   Aggregates the results.
    *   Writes the aggregated results (original domain + enriched data) to the output CSV file.

## 4. Phased Implementation Plan

*   **Phase 1: Minimum Viable Product (MVP):**
    *   **Focus:** Process *one* entry from the CSV using the ADK structure.
    *   Implement basic versions of `CsvReaderAgent`, `CsvWriterAgent`.
    *   Implement a simple, *non-parallel* `EnricherAgent` that directly runs *one* instance of `fomc-research` for the first domain found.
    *   Define the root `SequentialAgent` (`CsvReaderAgent` -> `EnricherAgent` -> `CsvWriterAgent`).
    *   Update/create a runner script (e.g., `run_enrichment.py`) to execute this simple sequence via `adk run`.
    *   **Goal:** Verify core CSV I/O and single `fomc-research` agent invocation within the ADK sequential flow.

*   **Phase 2: Dynamic Parallelism:**
    *   **Focus:** Implement the full parallel processing logic.
    *   Modify `CsvReaderAgent` to handle all domains from the CSV.
    *   Replace the simple `EnricherAgent` with the `DynamicDispatcherAgent` as described in the architecture section. This agent will dynamically create the `ParallelAgent` with multiple `fomc-research` instances.
    *   Ensure careful management of `session.state` using unique keys (incorporating `run_id` and domain/worker identifier) to avoid collisions during parallel execution, following the pattern shown in the provided example.
    *   Adapt `CsvWriterAgent` to correctly aggregate results from the potentially numerous entries in `session.state`.
    *   Update the runner script.
    *   **Goal:** Achieve full parallel processing of the input CSV using dynamically created ADK agents.

*   **Phase 3: Refinement:**
    *   Implement robust error handling within each agent (e.g., catching exceptions during enrichment, logging errors).
    *   Add comprehensive logging throughout the workflow.
    *   Introduce configuration options (e.g., specifying input/output file paths via command-line arguments or environment variables).
    *   Potentially add status updates or progress reporting during the parallel execution phase.

## 5. Key Considerations & Best Practices (from ADK Example)
- **Fresh Agent Instances:** Always create *new* instances of the worker agent (`fomc-research`) for each task within the `DynamicDispatcherAgent` before adding them to the dynamically created `ParallelAgent`. Agent instances cannot be reused across different parent agents or runs.
- **Safe `session.state` Management:** Use unique prefixes/keys (e.g., `task:{run_id}:{domain}`, `result:{run_id}:{domain}`) when reading from or writing to `session.state` to prevent race conditions or data overwrites between concurrent agents.
- **ADK Observability:** This dynamic `ParallelAgent` approach maintains ADK's event logging and state tracking capabilities, providing better observability than manual `asyncio.gather`.