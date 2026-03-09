from abc import ABC, abstractmethod


class AbstractTranscriptionRepository(ABC):

    @abstractmethod
    async def save(self, recording_id: int, text: str, segments: list[dict]) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
