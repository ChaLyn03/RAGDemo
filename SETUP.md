# Setup and run guide

This guide lists the supported setups and how to run the pipeline in each mode.

## Minimal / secure environment (offline)
Use this when you cannot access the public internet. The stub provider is default and does not require an API key.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

nxrag assets/samples/nx_code/widget_housing_request.txt
```

## OpenAI provider (online)
Use this when you have internet access and want real API calls.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-openai.txt
pip install -e .

export NX_RAG_LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key_here

nxrag assets/samples/nx_code/widget_housing_request.txt
```

## Dev / tooling setup
Use this when you want formatting, linting, or tests.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

pre-commit install
pytest
```

## Running the sample
This uses the stub provider by default.

```bash
nxrag assets/samples/nx_code/widget_housing_request.txt
```

## Run outputs
Each run creates a folder under `var/runs/` with artifacts such as:
- `retrieved.json`
- `prompt.txt`
- `generation.json`
- `output.md`

## Provider selection
- Default: stub provider (deterministic, offline).
- OpenAI: set `NX_RAG_LLM_PROVIDER=openai` and install `requirements-openai.txt`.

## Configuration
See `configs/app.yaml` for model/provider defaults and output locations.
