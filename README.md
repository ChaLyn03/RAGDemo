# nxrag

Scaffold for a structured retrieval-augmented generation pipeline. The repository layout focuses on clear boundaries between ingestion, retrieval, prompting, validation, and rendering so new contributors can extend components independently. The current state ships a minimal demo that chunks a tiny corpus and renders a Markdown part description.

## Getting started
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. Copy `.env.example` to `.env` and update provider credentials as needed.
3. Run the CLI help to see available commands:
   ```bash
   nxrag --help
   ```
4. Execute the sample pipeline against a bundled request:
   ```bash
   python -m nxrag.cli assets/samples/nx_code/widget_housing_request.txt
   ```
   The rendered Markdown output is written under `var/runs/` with a timestamped filename.

## Layout highlights
- **configs/** contains the canonical application, logging, prompt, and retrieval configuration files.
- **assets/** holds curated, version-controlled corpus and sample inputs.
- **var/** is reserved for generated artifacts (indexes, runs, caches) and is ignored from version control.
- **src/nxrag/** implements the pipeline modules.
- **tools/** provides command-line utilities that wrap the library modules.

## Contributing
Formatting, linting, and type checks are configured through pre-commit. Install hooks with:
```bash
pre-commit install
```
