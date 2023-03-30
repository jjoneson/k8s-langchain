from typing import Any, Dict, List
from langchain.tools.base import BaseTool
from kubernetes import client
from pydantic import BaseModel
import yaml


class KubernetesOpsModel(BaseModel):
    """Base Representation of a Kubernetes Operation."""
    """The fact of the matter is, the kubernetes API spec is way too large to be useful within the context window of an LLM, so we have to wrap it."""
    
    available_operations = ["create", "read", "list", "update", "delete"]
    available_resource_types = ["service", "deployment", "pod"]
    k8s_client: client.ApiClient
    core_v1: client.CoreV1Api
    apps_v1: client.AppsV1Api

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_k8s_client(cls, k8s_client: client.ApiClient):
        """Create a new KubernetesOpsModel from a kubernetes client."""
        return cls(k8s_client=k8s_client, core_v1=client.CoreV1Api(k8s_client), apps_v1=client.AppsV1Api(k8s_client))

    def get_operations(self) -> str:
        """Return a comma separated list of available operations."""
        return ",".join(self.available_operations)
    
    def get_resources(self) -> str:
        """Return a comma separated list of available resources."""
        return ",".join(self.available_resource_types)

    def get_namespaces(self) -> str:
        """Return a comma separated list of available namespaces."""
        namespace_list = self.core_v1.list_namespace()
        return ",".join([namespace.metadata.name for namespace in namespace_list.items])
    
    def create_namespace(self, namespace: str) -> str:
        """Create a new namespace."""
        try:
            self.core_v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))
            return "Namespace created"
        except Exception as e:
            return f"Error: {e}"
        
    def get_resource_names(self, namespace: str, resource_type: str ) -> str:
        """Return a comma separated list of available resources."""
        try:
            if resource_type == "service":
                resource_list = self.core_v1.list_namespaced_service(namespace)
            elif resource_type == "deployment":
                resource_list = self.apps_v1.list_namespaced_deployment(namespace)
            elif resource_type == "pod":
                resource_list = self.core_v1.list_namespaced_pod(namespace)
            else:
                return "Invalid resource type"
            return ",".join([resource.metadata.name for resource in resource_list.items])
        except Exception as e:
            return f"Error getting object names for {resource_type} in {namespace}: {e}"
    
    def get_resource(self, namespace: str, resource_type: str, resource_name: str) -> str:
        """Run a get for the specified resource in the specified namespace."""
        try:
            if resource_type == "service":
                resource = self.core_v1.read_namespaced_service(resource_name, namespace)
            elif resource_type == "deployment":
                resource = self.apps_v1.read_namespaced_deployment(resource_name, namespace)
            elif resource_type == "pod":
                resource = self.core_v1.read_namespaced_pod(resource_name, namespace)
            else:
                return "Invalid resource type"
            return self.resource_to_output(resource)
        except Exception as e:
            return f"Error getting {resource_type}/{resource_name} in {namespace}: {e}"
        
    def resource_to_output(self, resource: Any) -> str:
        """Convert the resource to a yaml string."""
        # first convert to_dict, then to yaml
        d = resource.to_dict()
        clean_resource = self.remove_managed_fields_from_metadata(d)
        d = clean_dict(clean_resource)
        yaml_src = yaml.dump(d)
        # delete every line that contains null unless it has a - in it
        yaml_src = "\n".join([line for line in yaml_src.splitlines() if "null" not in line or "-" in line])
        return yaml_src
    
    def remove_managed_fields_from_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Remove the managedFields key from the metadata of the resource."""
        resource["metadata"]["managed_fields"] = None
        return resource

# recursively remove none values from a dict, and anything where all of the values are none
def clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively remove none values from a dict, and anything where all of the values are none."""
    clean = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, dict):
            v = clean_dict(v)
        if isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    i = clean_dict(i)            
        if v:
            clean[k] = v
    return clean


class KubernetesGetAvailableOperationsTool(BaseTool):
    """Tool for getting determining available operations."""
    name = "k8s_determine_operations"
    description = """
    Can be used to determine which operations available.
    Before calling this, you should know the resource you want to operate on.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.get_operations()

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class KubernetesGetAvailableResourceTypesTool(BaseTool):
    """Tool for getting available resource types."""
    name = "k8s_get_available_resource_types"
    description = """
    Can be used to list all resource types available to the tool.
    Returns a comma separated list of resource types.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.get_resources()

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class KubernetesGetAvailableNamespacesTool(BaseTool):
    """Tool for getting  a list of available namespaces."""
    name = "k8s_get_available_namespaces"
    description = """
    Can be used to list all available namespaces.
    Returns a comma separated list of namespaces.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.get_namespaces()

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)
    
class KubernetesCreateNamespaceTool(BaseTool):
    """Tool for creating a new namespace."""
    name = "k8s_create_namespace"
    description = """
    Can be used to create a new namespace.
    Input should be a string containing the name of the namespace to create.
    Returns a string indicating success or failure.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        return self.model.create_namespace(tool_input)

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class KubernetesGetObjectNamesTool(BaseTool):
    """Tool for getting the names of existing objects."""
    name = "k8s_get_object_names"
    description = """
    You should know the resource type and namespace before calling this tool.
    Can be used to list the names of resources with a given resource type in a given namespace.
    Input should be a string containing the namespace and resource type, separated by a comma.
    Returns a comma separated list of resource names.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        namespace, resource_type = tool_input.split(",")
        return self.model.get_resource_names(namespace, resource_type)

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class KubernetesGetResourceTool(BaseTool):
    """Tool for executing a get on a specific Kubernetes Resource."""
    name = "k8s_get_resource"
    description = """
    You should know the namespace, resource type, and object name before calling this tool.
    Executes a get in the specified namespace for the specified resource type, with the specified name.
    Input should be a string containing the namespace, resource type, and object name, separated by commas.
    Returns a yaml string containing the spec.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        namespace, resource_type, resource_name = tool_input.split(",")
        return self.model.get_resource(namespace, resource_type, resource_name)

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)






