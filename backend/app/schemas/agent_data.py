from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class AgentResponse:
    message: str
    tool_calls: list[dict] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)

with open("app/prompts/system_prompt.md", "r") as f:
    SYSTEM_PROMPT = f.read()
