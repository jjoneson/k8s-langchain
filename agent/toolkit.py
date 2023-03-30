from typing import List
from agent.base import create_kubernetes_agent

from tools.resource_selector.tool import K8sResourceSelectorTool
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.llms.base import BaseLLM
from langchain.requests import RequestsWrapper
from langchain.tools import BaseTool
from langchain.agents.agent import AgentExecutor
from langchain.tools.requests.tool import (
    RequestsDeleteTool,
    RequestsGetTool,
    RequestsPatchTool,
    RequestsPostTool,
    RequestsPutTool,
)

class RequestsToolkit(BaseToolkit):
    """Toolkit for making requests."""

    requests_wrapper: RequestsWrapper

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            RequestsGetTool(requests_wrapper=self.requests_wrapper),
            RequestsPostTool(requests_wrapper=self.requests_wrapper),
            RequestsPatchTool(requests_wrapper=self.requests_wrapper),
            RequestsPutTool(requests_wrapper=self.requests_wrapper),
            RequestsDeleteTool(requests_wrapper=self.requests_wrapper),
        ]

class K8sToolkit(BaseToolkit):
    """Kubernetes toolkit."""

    agent: AgentExecutor

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            K8sResourceSelectorTool(),
        ]
    
    @classmethod
    def from_llm(cls, llm: BaseLLM):
        agent = create_kubernetes_agent(llm)
        return cls(agent=agent)

