from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class AgentResponse:
    message: str
    tool_calls: list[dict] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"
with open(_PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()
