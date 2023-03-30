from typing import List
from tools.git_integrator.tool import GitModel, GitRepositoryAddFileTool, GitRepositoryCheckoutBranchTool, GitRepositoryCloneTool, GitRepositoryCreateBranchTool, GitRepositoryGetFileContentTool, GitRepositoryPullTool, GitRepositoryPushTool, GitRepositoryWriteFileTool

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

class GitIntegratorToolkit(BaseToolkit):
    """Toolkit for interacting with git repositories."""

    model: GitModel

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            GitRepositoryCloneTool(model=self.model),
            GitRepositoryCreateBranchTool(model=self.model),
            GitRepositoryCheckoutBranchTool(model=self.model),
            GitRepositoryPullTool(model=self.model),
            GitRepositoryPushTool(model=self.model),
            GitRepositoryAddFileTool(model=self.model),
            GitRepositoryGetFileContentTool(model=self.model),
            GitRepositoryWriteFileTool(model=self.model),
        ]