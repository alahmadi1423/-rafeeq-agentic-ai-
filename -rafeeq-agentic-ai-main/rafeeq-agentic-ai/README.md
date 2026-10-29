# Rafeeq — Agentic AI Municipal Assistant

Rafeeq (رفيق) is an educational prototype of a bilingual municipal-permit assistant. It demonstrates how an AI agent can retrieve policy information, validate application details, prepare a structured draft, and pause for human review before any consequential action.

> **Educational demo only:** Madar and its policies are fictional. All policy content and applicant examples are synthetic. Rafeeq does not submit applications to a government service or issue permits.

## Overview

Municipal-permit processes can involve questions about requirements, missing information, and application preparation. A general-purpose chatbot may give unsupported answers or imply that an action has been completed when it has not.

Rafeeq explores a more controlled approach: combine local policy tools and validation logic with an AI agent, return structured results, and keep human approval separate from draft preparation.

## Features

- **Policy lookup:** retrieve information from a local, synthetic food-truck permit policy.
- **Application validation:** identify missing or invalid fields using the project's tools.
- **Structured drafts:** prepare an application draft for review rather than claiming it has been submitted.
- **Rule-based mode:** run a deterministic demo without an API key.
- **LLM tool-calling mode:** use OpenRouter to let a model select from the available tools.
- **Arabic web interface:** a Flask-based right-to-left interface displays the response, policy results, and a short tool trace when available.
- **Automated tests:** tests cover the tools and rule-based agent.

## How it works

1. The user asks a question or provides draft application details.
2. Rafeeq consults the local policy and validation tools.
3. The rule-based agent or OpenRouter-powered agent produces a response.
4. The interface presents relevant results and a structured draft where applicable.
5. A human reviews the draft. Preparing a draft does not submit an application or grant a permit.

## Technology

- Python 3.11+
- Flask for the local web interface
- OpenAI-compatible client and OpenRouter for model-powered tool calling
- Pytest for automated tests
- Local synthetic policy data

## Requirements

- Python 3.11 or a compatible version
- `pip`
- An OpenRouter API key for the model-powered agent and any features that require live model access

## Run locally

From the project root:

```bash
python -m pip install openai pytest
PYTHONPATH=. python -m pytest -v
```

Start the Arabic web interface:

```bash
PYTHONPATH=. python -m app.web_app
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

To use the OpenRouter agent, set `OPENROUTER_API_KEY` in your shell or environment configuration before starting the app. Never commit API keys, secrets, or populated `.env` files to the repository.

Example Python usage:

```python
from app.openrouter_agent import run_openrouter_agent

result = run_openrouter_agent(
    "ما المتطلبات الأساسية لتصريح عربة طعام؟"
)
print(result["answer"])
```

The agent defaults to the `openrouter/free` model router. Available models, routing, rate limits, and free endpoint availability can change over time.

## Run in Google Colab

If you are using the project in Colab, first change to the directory containing the project, then install the dependencies and run the tests:

```python
%cd /content/-rafeeq-agentic-ai/rafeeq-agentic-ai
%pip install -q openai pytest
```

```bash
!PYTHONPATH="$PWD" python -m pytest -q
```

For model-powered usage, add `OPENROUTER_API_KEY` to **Colab Secrets** and load it without hard-coding the key in a notebook:

```python
from google.colab import userdata
import os

os.environ["OPENROUTER_API_KEY"] = userdata.get("OPENROUTER_API_KEY")
```

The rule-based demo does not require an API key.

## Project structure

```text
app/
  tools.py
  agent.py
  llm_agent.py
  openrouter_agent.py
  web_app.py
policies/
  food_truck_policy.md
tests/
  test_tools.py
  test_agent.py
```

## Security and limitations

- **Synthetic data only:** the policy and applicant examples are fictional and are not official Saudi municipal requirements.
- **Drafts are not submissions:** the prototype does not connect to a government system and cannot issue a permit.
- **Protect API keys:** use environment variables or a secrets manager; do not commit credentials or populated environment files.
- **Tool boundaries:** model tool calls are limited to the tools implemented by the application; errors shown to the model or interface are sanitized.
- **Local demo controls:** the web demo includes basic request-size and per-process rate limits. These are not a substitute for production authentication, shared rate limiting, or deployment-level security controls.
- **Prototype status:** local educational data and a lightweight web server are intended for learning and demonstration, not production use.

## Potential next steps

- Add a documented setup script and a single configuration path for local and Colab usage.
- Expand tests to cover model-agent tool selection, invalid inputs, and error handling.
- Add evaluation cases for Arabic and English policy questions, tool-use accuracy, and unsupported claims.
- If the project is ever adapted for real services, add proper authentication, authorization, persistent storage, privacy review, monitoring, and human-governed workflows before connecting to external systems.

## Acknowledgements

This project is an independent educational prototype inspired by agentic AI concepts. It is not affiliated with or endorsed by any government authority.