# Rafeeq — Agentic AI Permit Assistant

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?logo=flask&logoColor=white)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-6566F1)
![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)
![Status](https://img.shields.io/badge/Status-Educational_Prototype-orange)

Rafeeq (رفيق) is an educational agentic AI prototype that helps users explore the requirements for a **fictional food-truck permit**. It combines local policy retrieval, application-field validation, draft preparation, and an optional OpenRouter-powered tool-calling agent.

> [!NOTE]
> This is an independent learning project. The municipality, policy, and example applicant data are fictional and synthetic. Rafeeq is not an official government service and does not submit applications or issue permits.

## Problem Statement

Permit processes can involve questions about requirements and missing application details. A general-purpose chatbot may respond without grounding its answer in the available policy or imply that an application has been submitted when it has not.

Rafeeq demonstrates a more controlled workflow: use a local policy tool for policy-related questions, validate required fields with application logic, and prepare a local draft that remains unsubmitted for human review.

## Features

### Policy and application support
- **Local policy search:** searches the project's synthetic food-truck policy document.
- **Application validation:** checks required fields and identifies missing, non-text, or overlong values.
- **Draft preparation:** creates a structured local draft only when required fields pass validation.
- **Explicit draft status:** drafts remain marked as awaiting approval; the project does not submit them to an external service.

### Agent modes
- **Rule-based agent:** deterministic keyword routing for a small set of supported Arabic and English requests.
- **OpenRouter tool-calling agent:** lets a language model select from a defined set of local tools.
- **Tool argument checks:** validates model-generated tool names and argument shapes before dispatch.
- **Bounded requests:** limits message size, tool-call batches, and tool rounds.

### Web interface and tests
- **Arabic-first web app:** Flask serves the local interface and a chat endpoint.
- **Basic demo protections:** request-size limits and a per-process rate limiter.
- **Automated tests:** Pytest tests cover policy search, application validation, draft behavior, rule-based routing, and tool argument validation.

## How It Works

1. The user asks a question or requests help preparing a food-truck application.
2. Rafeeq searches the local synthetic policy or validates the supplied application fields.
3. In model-powered mode, OpenRouter returns a response and may request one of the registered tools.
4. Rafeeq checks the tool arguments and runs the matching local function.
5. The user receives the answer or draft status. A prepared draft is **not** an official submission or permit approval.

## Architecture and Tools

| Component | Responsibility | Boundary |
|---|---|---|
| `search_policies` | Searches local Markdown policy content | Returns synthetic policy text; it is not an official source |
| `validate_application` | Checks required applicant, location, activity, and contact fields | Performs field validation only |
| `create_application_draft` | Creates a structured local draft | Does not submit or approve an application |
| Rule-based agent | Routes supported requests using simple rules | Limited intent recognition; not a general reasoning engine |
| OpenRouter agent | Calls a configured model and processes tool calls | Model output is untrusted and tool arguments are checked |
| Flask web app | Serves the UI and `/chat` endpoint | Intended for local demonstration, not public deployment |

### Guardrails and limitations

- **Synthetic policy:** retrieved content is fictional and must not be treated as actual municipal requirements.
- **No external actions:** the prototype has no government-system integration and cannot submit, approve, or issue permits.
- **Human review:** draft creation is separate from approval and submission.
- **Tool boundaries:** only registered tools are dispatched; tool arguments are validated before execution.
- **Secrets:** the OpenRouter API key must be provided through an environment variable and never committed to source control.
- **Web security:** the built-in request-size and rate limits are basic, in-process controls. They are not a replacement for authentication, production-grade rate limiting, monitoring, or deployment hardening.
- **Model availability:** model names, free routing, rate limits, and provider availability may change.

## Technology Stack

- **Python** — application and agent logic
- **Flask** — local web interface and chat endpoint
- **OpenAI-compatible Python client + OpenRouter** — optional model-powered tool calling
- **Pytest** — automated tests
- **Markdown** — local synthetic policy data

## Getting Started

### Requirements

- Python 3.11 or newer
- `pip`
- An OpenRouter API key for model-powered mode

### Install dependencies

Run these commands from the directory containing the `app/`, `policies/`, and `tests/` folders:

```bash
python -m pip install flask openai pytest
```

### Configure OpenRouter

Set your API key in the environment before starting the app.

**macOS / Linux**
```bash
export OPENROUTER_API_KEY="your-key"
```

**Windows PowerShell**
```powershell
$env:OPENROUTER_API_KEY="your-key"
```

Do not put a real key in your source code, README, screenshots, or Git commits.

### Run the web app

```bash
PYTHONPATH=. python -m app.web_app
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The server binds to localhost for local demonstration.

### Run the tests

```bash
PYTHONPATH=. python -m pytest -v
```

The tests are designed to run locally without calling the live OpenRouter service. The model-powered web chat itself requires a valid API key and provider availability.

## Example

A user can ask in Arabic:

```text
ما المتطلبات الأساسية لتصريح عربة طعام؟
```

Or request a draft after supplying all required fields:

```python
from app.tools import create_application_draft

application = {
    "applicant_name": "Demo User",
    "location": "Demo Location",
    "activity": "Food truck",
    "contact": "demo@example.com",
}

result = create_application_draft(application)
print(result["status"])     # awaiting_approval
print(result["submitted"])  # False
```

Use synthetic example details only.

## Project Structure

```text
.
├── README.md
├── app/
│   ├── tools.py
│   ├── agent.py
│   ├── llm_agent.py
│   ├── openrouter_agent.py
│   └── web_app.py
├── policies/
│   └── food_truck_policy.md
└── tests/
    ├── test_tools.py
    ├── test_agent.py
    └── test_openrouter_agent.py
```

## Future Improvements

- Add evaluation scenarios for Arabic and English policy questions, tool-selection accuracy, and unsupported claims.
- Expand the policy search beyond simple keyword matching.
- Add integration tests for web request validation and model-provider failures.
- Document and standardize dependency management and configuration for local and notebook-based workflows.
- Before any real-world adaptation, add robust authentication and authorization, privacy review, durable audit logging, monitoring, and a formal human-approval workflow.

## Acknowledgements

Rafeeq is an independent educational prototype inspired by agentic AI concepts. It is not affiliated with or endorsed by any municipality or government authority.
