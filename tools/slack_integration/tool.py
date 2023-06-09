from slack_sdk import WebClient
from langchain.tools.base import BaseTool
from pydantic import BaseModel

class SlackModel(BaseModel):
    """Model for slack integration."""
    client: WebClient

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_client(cls, client: WebClient):
        """Create a model from a client."""
        return cls(client=client)
    
    def send_message(self, message: str, channel: str, thread_ts: str | None = None) -> str:
        """Send a message to slack."""
        try: 
            self.client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts)
            return "Message sent"
        except Exception as e:
            return f"Error sending slack message: {e}"

class SlackSendMessageTool(BaseTool):
    """Tool for sending a message to slack."""
    name = "slack_send_message"
    description = """
    Only use this tool if you are absolutely sure you want to send a message to slack.
    Can be used to send a message in Slack.
    Input should be a string.
    """
    model: SlackModel
    thread_ts: str | None = None
    channel: str | None = None

    def _run(self, tool_input: str) -> str:
        """Send a message to slack."""
        # the input has newlines as literal \n, so we need to replace them with actual newlines
        tool_input = tool_input.replace("\\n", "\n")
        return self.model.send_message(tool_input, self.channel, self.thread_ts)
    
    async def _arun(self, tool_input: str) -> str:
        """Send a message to slack."""
        return self._run(tool_input)
    