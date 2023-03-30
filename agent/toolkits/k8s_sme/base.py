from typing import Optional, List, Any

from langchain.agents.agent import AgentExecutor
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.callbacks.base import BaseCallbackManager
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS

from agent.toolkits.k8s_sme.prompt import K8S_SME_PREFIX, K8S_SME_SUFFIX
from agent.toolkits.k8s_sme.toolkit import KubernetesSMEToolkit

def create_k8s_sme_agent(
        llm: BaseLLM,
        toolkit: KubernetesSMEToolkit,
        callback_manager: Optional[BaseCallbackManager] = None,
        prefix: str = K8S_SME_PREFIX,
        suffix: str = K8S_SME_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs: Any,
) -> AgentExecutor:
    """Create an agent for acting as a Kubernetes Subject Matter Expert."""
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
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=toolkit.get_tools(), verbose=verbose, callback_manager=callback_manager)