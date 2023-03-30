from langchain.agents import initialize_agent, Tool
from langchain.tools import BaseTool
from langchain.llms import OpenAI

class K8sResourceSelectorTool(BaseTool):
    """Tool for selecting which k8s resource to use."""
    name = "K8sResourceSelector"
    description = "useful for selecting which kubernetes resource a user wants to interact with"

    def _run(self, query: str) -> str:
        """Run the tool."""
        return "hello world"



    
