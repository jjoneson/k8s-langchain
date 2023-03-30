import os
import threading

from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from listeners.agent_listener import AgentListener
from langchain.agents.agent import AgentExecutor


class SlackListener(AgentListener):
    def __init__(self, agent: AgentExecutor):
        self.agent = agent
        # Initialize SocketModeClient with an app-level token + WebClient
        self.client = SocketModeClient(
            # This app-level token will be used only for establishing a connection
            app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
            # You will be using this WebClient for performing Web API calls in listeners
            web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
        
        )
        
    def on_message(self, message) -> str:
        res = self.agent({"input": message})
        return parse_intermediate_steps_into_slack_message(res["intermediate_steps"])


    def listen(self, interrupt: threading.Event):
        self.client.socket_mode_request_listeners.append(self.process)
        self.client.connect()
        interrupt.wait()

    def start(self) -> threading.Event:
    # run listen in a separate thread
        interrupt = threading.Event()
        thread = threading.Thread(target=self.listen, args=(interrupt,))
        thread.start()
        return interrupt

    def process(self, client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            # Add a reaction to the message if it's a new message
            if req.payload["event"]["type"] == "message" or req.payload["event"]["type"] == "app_mention"\
                and req.payload["event"].get("subtype") is None:
                # client.web_client.reactions_add(
                #     name="eyes",
                #     channel=req.payload["event"]["channel"],
                #     timestamp=req.payload["event"]["ts"],
                # )
                # reply to the message with an acknowledgement
                
                client.web_client.chat_postMessage(
                    channel=req.payload["event"]["channel"],
                    thread_ts=req.payload["event"]["ts"],
                    text="Let me think about that...")
                
                message = req.payload["event"]["text"]

                # remove the bot mention
                if req.payload["event"]["type"] == "app_mention":
                    message = message.split(" ", 1)[1]
                
                reply = self.on_message(message)
                # the reply has newlines as literal \n, so we need to replace them with actual newlines
                reply = reply.replace("\\n", "\n")
                client.web_client.chat_postMessage(
                    channel=req.payload["event"]["channel"],
                    thread_ts=req.payload["event"]["ts"],
                    text=reply)
        if req.type == "interactive" \
            and req.payload.get("type") == "shortcut":
            if req.payload["callback_id"] == "hello-shortcut":
                # Acknowledge the request
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)
                # Open a welcome modal
                client.web_client.views_open(
                    trigger_id=req.payload["trigger_id"],
                    view={
                        "type": "modal",
                        "callback_id": "hello-modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Greetings!"
                        },
                        "submit": {
                            "type": "plain_text",
                            "text": "Good Bye"
                        },
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Hello!"
                                }
                            }
                        ]
                    }
                )

        if req.type == "interactive" \
            and req.payload.get("type") == "view_submission":
            if req.payload["view"]["callback_id"] == "hello-modal":
                # Acknowledge the request and close the modal
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)



def parse_intermediate_steps_into_slack_message(steps) -> str:
    """steps is a NamedTuple with fields that looks like this:
    [(AgentAction(tool='Search', tool_input='Leo DiCaprio girlfriend', log=' I should look up who Leo DiCaprio is dating\nAction: Search\nAction Input: "Leo DiCaprio girlfriend"'), 'Camila Morrone'), (AgentAction(tool='Search', tool_input='Camila Morrone age', log=' I should look up how old Camila Morrone is\nAction: Search\nAction Input: "Camila Morrone age"'), '25 years'), (AgentAction(tool='Calculator', tool_input='25^0.43', log=' I should calculate what 25 years raised to the 0.43 power is\nAction: Calculator\nAction Input: 25^0.43'), 'Answer: 3.991298452658078\n')]
    """
    message = ""
    for step in steps:
        message += f"{step[0].log}\n"
        message += f"Answer: {step[1]}\n"
    return message

