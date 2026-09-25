from abc import ABC

class BaseTool(ABC):
    def __init__(self, name:str, description:str, **kwargs):
        self.name = name
        self.description = description

    def execute(self, **kwargs):
        raise NotImplementedError("Subclasses must implement the execute method.")