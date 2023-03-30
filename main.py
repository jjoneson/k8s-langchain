from agent.factory import AgentFactory
from listeners.slack_listener import SlackListener
from listeners.terminal_listener import TerminalListener

# turn on debug logging
# import logging
# logging.basicConfig(level=logging.DEBUG)

# slack_listener = SlackListener(AgentFactory())
# interrupt = slack_listener.start()
terminal_listener = TerminalListener(AgentFactory())
interrupt = terminal_listener.start()
# block until keyboard interrupt
interrupt.wait()

