from agent.factory import AgentFactory
from listeners.slack_listener import SlackListener
from listeners.terminal_listener import TerminalListener
from listeners.voice_listener import VoiceListener
import pyttsx3
from pyttsx3.voice import Voice

# turn on debug logging
# import logging
# logging.basicConfig(level=logging.DEBUG)


# engine = pyttsx3.init(driverName="nsss", debug=True)
# voices = engine.getProperty('voices')
# for voice in voices:
#     try:
#         engine.setProperty('voice', voice.id)
#         print(f"Voice Id: {voice.id}, voice name: {engine.getProperty('voice')}")
#     except Exception as e:
#         print(f"Error setting voice: {e}")




listener = VoiceListener(AgentFactory())
interrupt = listener.start()
# block until keyboard interrupt
interrupt.wait()

