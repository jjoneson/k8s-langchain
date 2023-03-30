from langchain import OpenAI
from langchain.tools.base import BaseTool
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

from doc_indexes.k8s_index import KubernetesIndex

class KubernetesSMEModel(BaseModel):
    index: KubernetesIndex

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_index(cls, index: KubernetesIndex):
        return cls(index=index)

    def query(self, query: str) -> str:
        retriever = self.index.vectordb.as_retriever()
        qa =  RetrievalQA.from_chain_type(llm=ChatOpenAI(), chain_type="stuff", retriever=retriever)
        return qa.run(query)
    

class KubernetesSMETool(BaseTool):
    name = "k8s_sme"
    description = """
    Tool for retrieving answers from the Kubernetes Subject Mattter Expert.
    Input should be a string.
    """
    model: KubernetesSMEModel

    def _run(self, tool_input: str) -> str:
        """Query the SME."""
        # the input has newlines as literal \n, so we need to replace them with actual newlines
        tool_input = tool_input.replace("\\n", "\n")
        return self.model.query(tool_input)
    
    async def _arun(self, tool_input: str) -> str:
        """Query the SME."""
        return self._run(tool_input)
