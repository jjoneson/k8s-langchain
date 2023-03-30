from langchain.agents.agent import AgentExecutor

class AgentListener:
    def __init__(self, agent: AgentExecutor):
        self.agent = agent

    def on_message(self, message: str) -> str:
        return self.agent.run(message)