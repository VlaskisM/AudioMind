from abc import ABC, abstractmethod


class AbstractDiarizationRepository(ABC):

    @abstractmethod
    async def save(self, recording_id: int, speakers: list[dict], num_speakers: int): ...
