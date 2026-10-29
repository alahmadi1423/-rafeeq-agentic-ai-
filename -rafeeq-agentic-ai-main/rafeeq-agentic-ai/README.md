# Rafeeq — Agentic AI Municipal Assistant

Rafeeq is an educational prototype of an AI assistant for a fictional municipal food-truck permit service. It demonstrates local policy lookup, application validation, tool calling, and human approval checkpoints.

## Features

- Local synthetic policy lookup.
- Application validation with missing-field detection.
- Draft preparation with an explicit human-approval checkpoint.
- Rule-based demo agent that works without an API key.
- OpenRouter-powered agent using tool calling.
- Automated tests for the tools and rule-based agent.

## Important Data Notice

All policies, requirements, and applicant examples are synthetic and intended for education and testing only. They are not official Saudi municipal regulations.

Drafts are local educational records. The application tools do not submit applications to a government service or grant permits. Human review is required before any further action.

## Requirements

- Python 3.11 or a compatible version.
- pip.
- An OpenRouter API key for the web app and live model-powered agent.

Install the dependencies with `python -m pip install -r requirements.txt`.

## Run in Google Colab

Open the project notebook, if included in the repository, and run its cells in order.

To run the project from the repository directory:

    %cd /content/-rafeeq-agentic-ai/rafeeq-agentic-ai
    %pip install -q openai pytest

Run the tests:

    !PYTHONPATH="$PWD" python -m pytest -q

The rule-based demo does not require an API key.

### Configure OpenRouter

Store your `OPENROUTER_API_KEY` in Colab Secrets rather than writing it directly into a notebook cell.

After adding the secret, load it in a Python cell:

    from google.colab import userdata
    import os

    os.environ["OPENROUTER_API_KEY"] = userdata.get("OPENROUTER_API_KEY")

Then try the OpenRouter agent:

    from app.openrouter_agent import run_openrouter_agent

    result = run_openrouter_agent(
        "ما المتطلبات الأساسية لتصريح عربة طعام؟"
    )
    print(result["answer"])

The agent uses the `openrouter/free` model router by default. Available models and routing may change, and free endpoints may have usage limits or availability restrictions.

## Run Locally

From the project root, install the dependencies:

    python -m pip install openai pytest

Run the automated tests:

    PYTHONPATH=. python -m pytest -v

To use the OpenRouter agent locally, set `OPENROUTER_API_KEY` as an environment variable using your operating system's environment or secrets manager. Never commit API keys or `.env` files.

## Project Structure

    app/
      tools.py
      agent.py
      llm_agent.py
      openrouter_agent.py
    policies/
      food_truck_policy.md
    tests/
      test_tools.py
      test_agent.py

## Web UI

Run the Arabic right-to-left Flask interface from the project root with `PYTHONPATH=. python -m app.web_app`, then open `http://127.0.0.1:5000`. The UI displays a structured draft, policy results, and a short tool trace when returned by the model.

The demo web endpoint limits message size and applies a lightweight per-process request limit. The rate limiter is not shared across workers and is not a substitute for production authentication, reverse-proxy controls, or a persistent rate-limit store.

## Security and Limitations

- API keys must be kept in environment variables or a secrets manager.
- `.env`, Python cache files, and test cache files are excluded through `.gitignore`.
- Tool execution uses local educational data.
- Tool calls are allowlisted, message and field sizes are bounded, and tool errors shown to the model/UI are sanitized.
- The web demo has a lightweight in-memory rate limit; it is intended for local use only.
- Draft preparation does not mean an application was submitted or approved.
- The project is a prototype, not a production municipal service.

## Project Status

The prototype includes local tools, a rule-based agent, an OpenRouter tool-calling agent, and automated tests. MCP integration, advanced retrieval and evaluation, and a production API remain potential future improvements.
