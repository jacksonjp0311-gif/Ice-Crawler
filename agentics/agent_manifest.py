from dataclasses import asdict, dataclass
from typing import List

@dataclass(frozen=True)
class AgentFile:
    path: str
    sha256: str
    size_kb: float

@dataclass(frozen=True)
class AgentTask:
    agent_id: str
    depth: int
    coherence_weight: float
    total_kb: float
    files: List[AgentFile]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["files"] = [asdict(file) for file in self.files]
        return data
