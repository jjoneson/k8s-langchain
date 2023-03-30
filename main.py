from agent.factory import AgentFactory
from listeners.slack_listener import SlackListener

# turn on debug logging
# import logging
# logging.basicConfig(level=logging.DEBUG)

slack_listener = SlackListener(AgentFactory())
interrupt = slack_listener.start()
# block until keyboard interrupt
interrupt.wait()

