from dipy_ai.tools import BaseTool

class MachineContextTool(BaseTool):
    def __init__(self, 
                name: str = "Machine Context Tool", 
                description: str = "A tool for retrieving the context of the machine."):
        super().__init__(name, description)

    def execute(self, *args, **kwargs):
        return "Machine information"