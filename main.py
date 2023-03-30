from agent.factory import AgentFactory
from listeners.slack_listener import SlackListener

slack_listener = SlackListener(AgentFactory())
interrupt = slack_listener.start()
# block until keyboard interrupt
interrupt.wait()

