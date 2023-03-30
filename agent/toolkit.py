from typing import List
from tools.k8s_operations.tool import KubernetesCreateNamespaceTool, KubernetesGetAvailableNamespacesTool, KubernetesGetAvailableOperationsTool, KubernetesGetObjectNamesTool, KubernetesGetAvailableResourceTypesTool, KubernetesGetPodLogsTool, KubernetesGetPodNameLikeTool, KubernetesGetResourceTool, KubernetesOpsModel

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

    
class K8sOperationsToolkit(BaseToolkit):
    """Toolkit for deciding which k8s operation to perform."""

    model: KubernetesOpsModel

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            KubernetesGetAvailableResourceTypesTool(model=self.model),
            KubernetesGetAvailableNamespacesTool(model=self.model),
            KubernetesGetObjectNamesTool(model=self.model),
            KubernetesGetPodNameLikeTool(model=self.model),
            KubernetesGetPodLogsTool(model=self.model),
            KubernetesGetAvailableOperationsTool(model=self.model),
            KubernetesGetResourceTool(model=self.model),
        ]
