import threading
from agent.factory import AgentFactory
from listeners.agent_listener import AgentListener

class TerminalListener(AgentListener):
    def __init__(self, factory: AgentFactory):
        super().__init__(factory)

    def listen(self, interrupt: threading.Event):
        while not interrupt.is_set():
            message = input("Enter your message: ")
            agent = self.factory.new_k8s_engineer(handlers=None)
            agent({"input": message})
            del agent

    def start(self) -> threading.Event:
        # run listen in a separate thread
        interrupt = threading.Event()
        thread = threading.Thread(target=self.listen, args=(interrupt,))
        thread.start()
        return interrupt
    
        