from typing import Optional, List, Any

from langchain.agents.agent import AgentExecutor
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.callbacks.base import BaseCallbackManager
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from agent.toolkits.git_integrator.pompt import GIT_PREFIX, GIT_SUFFIX

from agent.toolkits.git_integrator.toolkit import GitIntegratorToolkit

def create_git_integration_toolkit(
        llm: BaseLLM,
        toolkit: GitIntegratorToolkit,
        callback_manager: Optional[BaseCallbackManager] = None,
        prefix: str = GIT_PREFIX,
        suffix: str = GIT_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs: Any,
) -> AgentExecutor:
    """Create an agent for integrating with git repositories."""
    tools = toolkit.get_tools()
    prompt = ZeroShotAgent.create_prompt(tools=tools,
                                         prefix=prefix,
                                         suffix=suffix,
                                         format_instructions=format_instructions,
                                         input_variables=input_variables,
                                         )
    llm_chain = LLMChain(llm=llm,
                         prompt=prompt,
                         callback_manager=callback_manager,
                         )
    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(llm_chain=llm_chain,
                          allowed_tools=tool_names, **kwargs)
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=toolkit.get_tools(), callback_manager=callback_manager, verbose=verbose)