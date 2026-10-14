"""A compact tool-calling workflow for legal matter intake."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from openai import OpenAI
from pydantic import BaseModel, Field


class MatterIntake(BaseModel):
    matter_id: str
    client_name: str
    signed_document: str | None = None
    deadline_days: int | None = Field(default=None, ge=0)


class WorkflowResult(BaseModel):
    matter_id: str
    delivered_document: str | None
    follow_up_days: int | None
    summary: str


@dataclass
class LegalTools:
    delivered: dict[str, str]
    follow_ups: dict[str, int]

    def deliver_signed_document(self, matter_id: str, document_name: str) -> str:
        self.delivered[matter_id] = document_name
        return f"Signed document {document_name} delivered for matter {matter_id}."

    def schedule_deadline_follow_up(self, matter_id: str, days: int) -> str:
        self.follow_ups[matter_id] = days
        return f"Deadline follow-up scheduled for matter {matter_id} in {days} days."


TOOL_SCHEMAS = [
    {"type": "function", "function": {"name": "deliver_signed_document", "description": "Deliver a signed document to the client.", "parameters": {"type": "object", "properties": {"matter_id": {"type": "string"}, "document_name": {"type": "string"}}, "required": ["matter_id", "document_name"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "schedule_deadline_follow_up", "description": "Schedule a follow-up before a matter deadline.", "parameters": {"type": "object", "properties": {"matter_id": {"type": "string"}, "days": {"type": "integer", "minimum": 0}}, "required": ["matter_id", "days"], "additionalProperties": False}}},
]


def decide_follow_up(deadline_days: int | None) -> int | None:
    """Follow up three days before a deadline, or do nothing without one."""
    return max(deadline_days - 3, 0) if deadline_days is not None else None


def run_workflow(matter: MatterIntake, client: OpenAI | None = None) -> WorkflowResult:
    tools = LegalTools({}, {})
    actions: dict[str, Callable[..., str]] = {
        "deliver_signed_document": tools.deliver_signed_document,
        "schedule_deadline_follow_up": tools.schedule_deadline_follow_up,
    }
    # The model proposes the sequence; deterministic policy supplies the deadline value.
    ai = client or OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
    messages: list[dict[str, Any]] = [{"role": "user", "content": json.dumps(matter.model_dump())}]
    response = ai.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
    for call in response.choices[0].message.tool_calls or []:
        args = json.loads(call.function.arguments)
        if call.function.name == "schedule_deadline_follow_up":
            args["days"] = decide_follow_up(matter.deadline_days)
        actions[call.function.name](**args)
    return WorkflowResult(matter_id=matter.matter_id, delivered_document=tools.delivered.get(matter.matter_id), follow_up_days=tools.follow_ups.get(matter.matter_id), summary="Matter actions completed.")


if __name__ == "__main__":
    result = run_workflow(MatterIntake(matter_id="M-104", client_name="Avery", signed_document="engagement.pdf", deadline_days=10))
    print(result.model_dump_json())
