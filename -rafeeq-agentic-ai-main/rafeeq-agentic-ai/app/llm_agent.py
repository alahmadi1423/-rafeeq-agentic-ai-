import json
import os
from typing import Any

from openai import OpenAI

from app.tools import (
    search_policies,
    validate_application,
    create_application_draft,
)


MAX_TOOL_STEPS = 4

TOOLS = [
    {
        "type": "function",
        "name": "search_policies",
        "description": (
            "Search the local synthetic policy documents. "
            "Use this for questions about requirements or policies."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The terms to search for."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "validate_application",
        "description": (
            "Check whether an application contains all required fields. "
            "Use only information supplied by the user."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "object",
                    "properties": {
                        "applicant_name": {"type": "string"},
                        "location": {"type": "string"},
                        "activity": {"type": "string"},
                        "contact": {"type": "string"}
                    },
                    "required": [
                        "applicant_name",
                        "location",
                        "activity",
                        "contact"
                    ],
                    "additionalProperties": False
                }
            },
            "required": ["application"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "create_application_draft",
        "description": (
            "Prepare a local application draft when the user explicitly "
            "asks for one. This does not submit the application. "
            "The returned draft must remain awaiting human approval."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "object",
                    "properties": {
                        "applicant_name": {"type": "string"},
                        "location": {"type": "string"},
                        "activity": {"type": "string"},
                        "contact": {"type": "string"}
                    },
                    "required": [
                        "applicant_name",
                        "location",
                        "activity",
                        "contact"
                    ],
                    "additionalProperties": False
                }
            },
            "required": ["application"],
            "additionalProperties": False
        },
        "strict": True
    }
]


INSTRUCTIONS = """
You are Rafeeq, an educational municipal-services assistant.

Rules:
- Reply in the language used by the user.
- Use search_policies for questions about policy requirements.
- Never invent requirements, applicant details, or search results.
- The available policy document is synthetic educational data,
  not an official Saudi regulation. State this when relevant.
- Use validate_application to check application fields.
- Create a draft only when the user explicitly asks for one.
- Creating a draft is not submitting an application.
- Never claim that an application was officially submitted or approved.
- Tool arguments must contain only information actually provided.
- If required application details are missing, ask the user for them.
- Do not claim a tool succeeded unless its result confirms that.
"""


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run only the tools explicitly registered by this application."""

    if name == "search_policies":
        return search_policies(arguments["query"])

    if name == "validate_application":
        return validate_application(arguments["application"])

    if name == "create_application_draft":
        return create_application_draft(arguments["application"])

    return {"ok": False, "error": "Unknown tool."}


def run_llm_agent(message: str) -> dict[str, Any]:
    """Run the LLM tool-calling loop with a strict step limit."""

    if not message or not message.strip():
        return {"ok": False, "error": "Please enter a question."}

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "ok": False,
            "error": "OPENAI_API_KEY is not configured."
        }

    model = os.environ.get("OPENAI_MODEL", "gpt-5.6-terra")
    client = OpenAI(api_key=api_key)

    conversation_input = [
        {"role": "user", "content": message.strip()}
    ]

    try:
        for step in range(MAX_TOOL_STEPS + 1):
            response = client.responses.create(
                model=model,
                instructions=INSTRUCTIONS,
                input=conversation_input,
                tools=TOOLS,
                tool_choice="auto",
            )

            calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not calls:
                return {
                    "ok": True,
                    "answer": response.output_text,
                    "tool_steps": step,
                    "model": model,
                }

            if step >= MAX_TOOL_STEPS:
                return {
                    "ok": False,
                    "error": "Maximum tool-call steps reached.",
                    "tool_steps": step,
                }

            # Preserve the model response, including its tool calls.
            conversation_input.extend(response.output)

            for call in calls:
                try:
                    arguments = json.loads(call.arguments)
                    result = execute_tool(call.name, arguments)
                    tool_output = json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    )
                except Exception as exc:
                    # Return a safe tool error to the model.
                    tool_output = json.dumps({
                        "ok": False,
                        "error": (
                            "Tool execution failed: "
                            + type(exc).__name__
                        )
                    })

                conversation_input.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": tool_output,
                })

        return {"ok": False, "error": "Agent stopped unexpectedly."}

    except Exception as exc:
        # Avoid exposing credentials or internal exception details.
        return {
            "ok": False,
            "error": "LLM request failed: " + type(exc).__name__,
        }
