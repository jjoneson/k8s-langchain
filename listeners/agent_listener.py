from agent.factory import AgentFactory

class AgentListener:
    factory: AgentFactory
    def __init__(self, factory: AgentFactory):
        self.factory = factory