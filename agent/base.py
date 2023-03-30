from typing import Optional, List, Any

from langchain.agents.agent import AgentExecutor
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.callbacks.base import BaseCallbackManager
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from agent.prompt import K8S_PREFIX, K8S_SUFFIX

from agent.toolkit import K8sOperationsToolkit


def create_kubernetes_agent(
        llm: BaseLLM,
        toolkit: K8sOperationsToolkit,
        callback_manager: Optional[BaseCallbackManager] = None,
        prefix: str = K8S_PREFIX,
        suffix: str = K8S_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs: Any,
) -> AgentExecutor:
    """Create an agent for interacting with a kubernetes cluster."""
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
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=toolkit.get_tools(), verbose=verbose)
