from typing import List
from tools.k8s_explorer.tool import KubernetesGetAvailableNamespacesTool, KubernetesGetAvailableOperationsTool, KubernetesGetObjectNamesTool, KubernetesGetAvailableResourceTypesTool, KubernetesGetPodLogsTool, KubernetesGetPodNameLikeTool, KubernetesGetResourceTool, KubernetesOpsModel

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools import BaseTool

    
class K8sExplorerToolkit(BaseToolkit):
    """Toolkit for deciding which k8s operation to perform."""

    model: KubernetesOpsModel
    callback_manager: BaseCallbackManager

    class Config:
        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            KubernetesGetAvailableResourceTypesTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetAvailableNamespacesTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetObjectNamesTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetPodNameLikeTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetPodLogsTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetAvailableOperationsTool(model=self.model, callback_manager=self.callback_manager),
            KubernetesGetResourceTool(model=self.model, callback_manager=self.callback_manager),
        ]
    
