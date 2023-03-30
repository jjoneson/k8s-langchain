from typing import List
from tools.git_integrator.tool import GitModel, GitRepositoryAddFileTool, GitRepositoryCheckoutBranchTool, GitRepositoryCloneTool, GitRepositoryCreateBranchTool, GitRepositoryGetFileContentTool, GitRepositoryPullTool, GitRepositoryPushTool, GitRepositoryWriteFileTool

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools import BaseTool

class GitIntegratorToolkit(BaseToolkit):
    """Toolkit for interacting with git repositories."""

    model: GitModel
    callback_manager: BaseCallbackManager

    class Config:
        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            GitRepositoryCloneTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryCreateBranchTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryCheckoutBranchTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryPullTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryPushTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryAddFileTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryGetFileContentTool(model=self.model, callback_manager=self.callback_manager),
            GitRepositoryWriteFileTool(model=self.model, callback_manager=self.callback_manager),
        ]