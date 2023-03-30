from gitlab import Gitlab, GitlabDeleteError
from langchain.tools.base import BaseTool
from pydantic import BaseModel


class GitlabModel(BaseModel):
    gl: Gitlab

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_gitlab(cls, gl: Gitlab):
        return cls(gl=gl)
    
    def list_projects(self, org_id: int) -> str:
        try:
            projects = self.gl.projects.list(organization_id=org_id)
            # return just the names of the projects
            return [project.name for project in projects]
        except GitlabDeleteError as e:
            return f"Error listing projects: {e}"
    
    def list_groups(self):
        try:
            groups = self.gl.groups.list()
            # return just the names of the groups
            return [group.name for group in groups]
        except GitlabDeleteError as e:
            return f"Error listing groups: {e}"
    
    def get_project_issues(self, project_id: int) -> str:
        try:
            issues = self.gl.projects.get(project_id).issues.list()
            # return just the names of the issues
            return [issue.title for issue in issues]
        except GitlabDeleteError as e:
            return f"Error listing issues: {e}"
    
    def create_project_issue(self, project_id: int, title: str, description: str) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.create(
                {"title": title, "description": description}
            )
            return issue.title
        except GitlabDeleteError as e:
            return f"Error creating issue: {e}"
    
    def change_issue_label(self, project_id: int, issue_id: int, label: str) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.get(issue_id)
            issue.labels = label
            issue.save()
            return issue.labels
        except GitlabDeleteError as e:
            return f"Error changing issue label: {e}"
    
    def close_issue(self, project_id: int, issue_id: int) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.get(issue_id)
            issue.state_event = "close"
            issue.save()
            return issue.state
        except GitlabDeleteError as e:
            return f"Error closing issue: {e}"
        
    def reopen_issue(self, project_id: int, issue_id: int) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.get(issue_id)
            issue.state_event = "reopen"
            issue.save()
            return issue.state
        except GitlabDeleteError as e:
            return f"Error reopening issue: {e}"
        
    def comment_on_issue(self, project_id: int, issue_id: int, comment: str) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.get(issue_id)
            issue.notes.create({"body": comment})
            return issue.notes.list()
        except GitlabDeleteError as e:
            return f"Error commenting on issue: {e}"
    
    def reply_to_issue_comment(self, project_id: int, issue_id: int, comment_id: int, reply: str) -> str:
        try:
            issue = self.gl.projects.get(project_id).issues.get(issue_id)
            issue.notes.get(comment_id).reply(reply)
            return issue.notes.list()
        except GitlabDeleteError as e:
            return f"Error replying to issue comment: {e}"
        
    def create_merge_request(self, project_id: int, title: str, description: str, source_branch: str, target_branch: str):
        try:
            merge_request = self.gl.projects.get(project_id).mergerequests.create(
                {"title": title, "description": description, "source_branch": source_branch, "target_branch": target_branch}
            )
            return merge_request.title
        except GitlabDeleteError as e:
            return f"Error creating merge request: {e}"
    
    def get_merge_requests(self, project_id: int) -> str:
        try:
            merge_requests = self.gl.projects.get(project_id).mergerequests.list()
            # return just the titles of the merge requests
            return [merge_request.title for merge_request in merge_requests]
        except GitlabDeleteError as e:
            return f"Error listing merge requests: {e}"
    
    def comment_on_merge_request(self, project_id: int, merge_request_id: int, comment: str) -> str:
        try:
            merge_request = self.gl.projects.get(project_id).mergerequests.get(merge_request_id)
            merge_request.notes.create({"body": comment})
            return merge_request.notes.list()
        except GitlabDeleteError as e:
            return f"Error commenting on merge request: {e}"
    
    def reply_to_merge_request_comment(self, project_id: int, merge_request_id: int, comment_id: int, reply: str) -> str:
        try:
            merge_request = self.gl.projects.get(project_id).mergerequests.get(merge_request_id)
            merge_request.notes.get(comment_id).reply(reply)
            return merge_request.notes.list()
        except GitlabDeleteError as e:
            return f"Error replying to merge request comment: {e}"
        
    def run_pipeline(self, project_id: int, ref: str) -> str:
        try:
            pipeline = self.gl.projects.get(project_id).pipelines.create({"ref": ref})
            return pipeline.status
        except GitlabDeleteError as e:
            return f"Error running pipeline: {e}"

class GitlabListProjectsTool(BaseTool):
    """Tool for listing all projects in a group."""
    name = "gitlab_list_projects"
    description = """
    You should know the group id before using this tool.
    Can be used to list all projects in a gitlab group.
    Input should be a gitlab group id.
    Returns a list of project names.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.list_projects(org_id=int(tool_input))
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabListGroupsTool(BaseTool):
    """Tool for listing all groups."""
    name = "gitlab_list_groups"
    description = """
    Can be used to list all groups in a gitlab instance.
    Input should None.
    Returns a list of group names.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.list_groups()
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class GitlabListIssuesTool(BaseTool):
    """Tool for listing all issues in a project."""
    name = "gitlab_list_issues"
    description = """
    You should know the project id before using this tool.
    Can be used to list all issues in a gitlab project.
    Input should be a gitlab project id.
    Returns a list of issue titles.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.list_issues(project_id=int(tool_input))
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabChangeIssueLabelTool(BaseTool):
    """Tool for changing the label of an issue in a project."""
    name = "gitlab_change_issue_label"
    description = """
    You should know the project id and issue id before using this tool.
    Can be used to change the label of an issue in a gitlab project.
    Input should be a gitlab project id, issue id, and new label.
    Returns a list of issue labels.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, issue_id, new_label = tool_input.split(",")
        # remove leading and trailing whitespace
        project_id = project_id.strip()
        issue_id = issue_id.strip()
        new_label = new_label.strip()

        return self.model.change_issue_label(project_id=int(project_id), issue_id=int(issue_id), new_label=new_label)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class GitlabListMergeRequestsTool(BaseTool):
    """Tool for listing all merge requests in a project."""
    name = "gitlab_list_merge_requests"
    description = """
    You should know the project id before using this tool.
    Can be used to list all merge requests in a gitlab project.
    Input should be a gitlab project id.
    Returns a list of merge request titles.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.get_merge_requests(project_id=int(tool_input))
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class GitlabCreateIssueTool(BaseTool):
    """Tool for creating an issue in a project."""
    name = "gitlab_create_issue"
    description = """
    You should know the project id before using this tool.
    Can be used to create an issue in a gitlab project.
    Input should be a comma separated list of gitlab project id, title, description
    Returns the title of the created issue.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, title, description = tool_input.split(",", 2)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        title = title.strip()
        description = description.strip()
        return self.model.create_project_issue(project_id=int(project_id), title=title, description=description)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabCommentOnIssueTool(BaseTool):
    """Tool for commenting on an issue in a project."""
    name = "gitlab_comment_on_issue"
    description = """
    You should know the project id and issue id before using this tool.
    Can be used to comment on an issue in a gitlab project.
    Input should be a comma separated list of gitlab project id, issue id, and comment
    Returns the comment.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, issue_id, comment = tool_input.split(",", 2)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        issue_id = issue_id.strip()
        comment = comment.strip()
        return self.model.comment_on_issue(project_id=int(project_id), issue_id=int(issue_id), comment=comment)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabReplyToIssueCommentTool(BaseTool):
    """Tool for replying to a comment on an issue in a project."""
    name = "gitlab_reply_to_issue_comment"
    description = """
    You should know the project id, issue id, and comment id before using this tool.
    Can be used to reply to a comment on an issue in a gitlab project.
    Input should be a comma separated list of gitlab project id, issue id, comment id, and reply
    Returns the reply.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, issue_id, comment_id, reply = tool_input.split(",", 3)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        issue_id = issue_id.strip()
        comment_id = comment_id.strip()
        reply = reply.strip()
        return self.model.reply_to_issue_comment(project_id=int(project_id), issue_id=int(issue_id), comment_id=int(comment_id), reply=reply)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabCreateMergeRequestTool(BaseTool):
    """Tool for creating a merge request in a project."""
    name = "gitlab_create_merge_request"
    description = """
    You should know the project id before using this tool.
    Can be used to create a merge request in a gitlab project.
    Input should be a comma separated list of gitlab project id, title, description, source branch, target branch
    Returns the title of the created merge request.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, title, description, source_branch, target_branch = tool_input.split(",", 4)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        title = title.strip()
        description = description.strip()
        source_branch = source_branch.strip()
        target_branch = target_branch.strip()
        return self.model.create_merge_request(project_id=int(project_id), title=title, description=description, source_branch=source_branch, target_branch=target_branch)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabCommentOnMergeRequestTool(BaseTool):
    """Tool for commenting on a merge request in a project."""
    name = "gitlab_comment_on_merge_request"
    description = """
    You should know the project id and merge request id before using this tool.
    Can be used to comment on a merge request in a gitlab project.
    Input should be a comma separated list of gitlab project id, merge request id, and comment
    Returns the comment.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, merge_request_id, comment = tool_input.split(",", 2)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        merge_request_id = merge_request_id.strip()
        comment = comment.strip()
        return self.model.comment_on_merge_request(project_id=int(project_id), merge_request_id=int(merge_request_id), comment=comment)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class GitlabReplyToMergeRequestCommentTool(BaseTool):
    """Tool for replying to a comment on a merge request in a project."""
    name = "gitlab_reply_to_merge_request_comment"
    description = """
    You should know the project id, merge request id, and comment id before using this tool.
    Can be used to reply to a comment on a merge request in a gitlab project.
    Input should be a comma separated list of gitlab project id, merge request id, comment id, and reply
    Returns the reply.
    """
    model: GitlabModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        project_id, merge_request_id, comment_id, reply = tool_input.split(",", 3)
        # remove any leading or trailing whitespace
        project_id = project_id.strip()
        merge_request_id = merge_request_id.strip()
        comment_id = comment_id.strip()
        reply = reply.strip()
        return self.model.reply_to_merge_request_comment(project_id=int(project_id), merge_request_id=int(merge_request_id), comment_id=int(comment_id), reply=reply)
    
    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

    
        
    
