from abc import ABC, abstractmethod

class Agent(ABC):
    name: str

    @abstractmethod
    async def run(self, **kwargs):
        """Execute agent task and return result"""