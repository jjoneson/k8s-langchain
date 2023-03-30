from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

from tools.gitlab_integration.tool import GitlabChangeIssueLabelTool, GitlabCommentOnIssueTool, GitlabCommentOnMergeRequestTool, GitlabCreateIssueTool, GitlabCreateMergeRequestTool, GitlabListGroupsTool, GitlabListIssuesTool, GitlabListMergeRequestsTool, GitlabListProjectsTool, GitlabModel, GitlabReplyToIssueCommentTool, GitlabReplyToMergeRequestCommentTool

class GitlabIntegrationToolkit(BaseToolkit):
    """Toolkit for interacting with gitlab."""

    model: GitlabModel

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            GitlabListProjectsTool(model=self.model),
            GitlabListGroupsTool(model=self.model),
            GitlabListIssuesTool(model=self.model),
            GitlabChangeIssueLabelTool(model=self.model),
            GitlabListMergeRequestsTool(model=self.model),
            GitlabCreateIssueTool(model=self.model),
            GitlabCommentOnIssueTool(model=self.model),
            GitlabReplyToIssueCommentTool(model=self.model),
            GitlabCreateMergeRequestTool(model=self.model),
            GitlabCommentOnMergeRequestTool(model=self.model),
            GitlabReplyToMergeRequestCommentTool(model=self.model),
        ]
        