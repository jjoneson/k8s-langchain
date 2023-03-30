from typing import Any, Dict, List
from langchain.tools.base import BaseTool
from kubernetes import client
from pydantic import BaseModel
import yaml


class KubernetesOpsModel(BaseModel):
    """Base Representation of a Kubernetes Operation."""
    """The fact of the matter is, the kubernetes API spec is way too large to be useful within the context window of an LLM, so we have to wrap it."""

    available_operations = ["create", "read", "list", "update", "delete", "logs"]
    core_v1_resource_types = [
        "configmap",
        "namespace",
        "persistentvolume",
        "persistentvolumeclaim",
        "pod",
        "secret",
        "serviceaccount",
        "service",
        "node",
    ]
    apps_v1_resource_types = [
        "daemonset",
        "deployment",
        "replicaset",
        "statefulset",
    ]
    batch_v1_resource_types = [
        "job",
        "cronjob",
    ]
    networking_v1_resource_types = [
        "ingress",
    ]
    rbac_v1_resource_types = [
        "clusterrole",
        "clusterrolebinding",
        "role",
        "rolebinding",
    ]
    available_resource_types = core_v1_resource_types + apps_v1_resource_types + \
        batch_v1_resource_types + networking_v1_resource_types + rbac_v1_resource_types
    k8s_client: client.ApiClient
    core_v1: client.CoreV1Api
    apps_v1: client.AppsV1Api
    batch_v1: client.BatchV1Api
    networking_v1: client.NetworkingV1Api
    rbac_v1: client.RbacAuthorizationV1Api

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_k8s_client(cls, k8s_client: client.ApiClient):
        """Create a new KubernetesOpsModel from a kubernetes client."""
        return cls(k8s_client=k8s_client, core_v1=client.CoreV1Api(k8s_client), apps_v1=client.AppsV1Api(k8s_client), batch_v1=client.BatchV1Api(k8s_client), networking_v1=client.NetworkingV1Api(k8s_client), rbac_v1=client.RbacAuthorizationV1Api(k8s_client))

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
    
    def get_logs(self, namespace: str, pod_name: str) -> str:
        """Get the logs for a pod."""
        # remove spaces
        namespace = namespace.replace(" ", "")
        pod_name = pod_name.replace(" ", "")
        try:
            return self.core_v1.read_namespaced_pod_log(pod_name, namespace, tail_lines=50)
        except Exception as e:
            return f"Error getting logs for pod {pod_name} in {namespace}: {e}"

    def create_namespace(self, namespace: str) -> str:
        """Create a new namespace."""
        try:
            self.core_v1.create_namespace(client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)))
            return "Namespace created"
        except Exception as e:
            return f"Error: {e}"

    def get_resource_list(self, namespace: str, resource_type: str) -> List[Any]:
        """Get a list of resources of a given type in a given namespace."""
        # remove spaces
        resource_type = resource_type.replace(" ", "")
        namespace = namespace.replace(" ", "")
        try:
            if resource_type == "configmap" or resource_type == "configmaps":
                resource_list = self.core_v1.list_namespaced_config_map(
                    namespace)
            elif resource_type == "namespace" or resource_type == "namespaces":
                resource_list = self.core_v1.list_namespace()
            elif resource_type == "persistentvolume" or resource_type == "persistentvolumes":
                resource_list = self.core_v1.list_persistent_volume()
            elif resource_type == "persistentvolumeclaim" or resource_type == "persistentvolumeclaims":
                resource_list = self.core_v1.list_namespaced_persistent_volume_claim(
                    namespace)
            elif resource_type == "pod" or resource_type == "pods":
                resource_list = self.core_v1.list_namespaced_pod(namespace)
            elif resource_type == "secret" or resource_type == "secrets":
                resource_list = self.core_v1.list_namespaced_secret(namespace)
            elif resource_type == "serviceaccount" or resource_type == "serviceaccounts":
                resource_list = self.core_v1.list_namespaced_service_account(
                    namespace)
            elif resource_type == "service" or resource_type == "services":
                resource_list = self.core_v1.list_namespaced_service(namespace)
            elif resource_type == "node" or resource_type == "nodes":
                resource_list = self.core_v1.list_node()
            elif resource_type == "daemonset" or resource_type == "daemonsets":
                resource_list = self.apps_v1.list_namespaced_daemon_set(
                    namespace)
            elif resource_type == "deployment" or resource_type == "deployments":
                resource_list = self.apps_v1.list_namespaced_deployment(
                    namespace)
            elif resource_type == "replicaset" or resource_type == "replicasets":
                resource_list = self.apps_v1.list_namespaced_replica_set(
                    namespace)
            elif resource_type == "statefulset" or resource_type == "statefulsets":
                resource_list = self.apps_v1.list_namespaced_stateful_set(
                    namespace)
            elif resource_type == "job" or resource_type == "jobs":
                resource_list = self.batch_v1.list_namespaced_job(namespace)
            elif resource_type == "cronjob" or resource_type == "cronjobs":
                resource_list = self.batch_v1.list_namespaced_cron_job(
                    namespace)
            elif resource_type == "ingress" or resource_type == "ingresses":
                resource_list = self.networking_v1.list_namespaced_ingress(
                    namespace)
            elif resource_type == "clusterrole" or resource_type == "clusterroles":
                resource_list = self.rbac_v1.list_cluster_role()
            elif resource_type == "clusterrolebinding" or resource_type == "clusterrolebindings":
                resource_list = self.rbac_v1.list_cluster_role_binding()
            elif resource_type == "role" or resource_type == "roles":
                resource_list = self.rbac_v1.list_namespaced_role(namespace)
            elif resource_type == "rolebinding" or resource_type == "rolebindings":
                resource_list = self.rbac_v1.list_namespaced_role_binding(
                    namespace)
            else:
                return "Invalid resource type"
            return resource_list.items
        except Exception as e:
            return f"Error getting object names for {resource_type} in {namespace}: {e}"
        
    def get_running_pod_names(self, pods: List[Any]) -> str:
        """Return a comma separated list of running pods."""
        return ",".join([pod.metadata.name for pod in pods if pod.status.phase == "Running"])

    def get_resource_names(self, namespace: str, resource_type: str) -> str:
        """Return a comma separated list of available resources."""
        # remove spaces
        resource_type = resource_type.replace(" ", "")
        namespace = namespace.replace(" ", "")
        try:
            return ",".join([resource.metadata.name for resource in self.get_resource_list(namespace, resource_type)])
        except Exception as e:
            return f"Error getting object names for {resource_type} in {namespace}: {e}"

    def get_resource(self, namespace: str, resource_type: str, resource_name: str) -> str:
        """Run a get for the specified resource in the specified namespace."""
        # remove spaces
        resource_type = resource_type.replace(" ", "")
        namespace = namespace.replace(" ", "")
        
        try:
            if resource_type == "configmap" or resource_type == "configmaps":
                resource = self.core_v1.read_namespaced_config_map(
                    resource_name, namespace)
            elif resource_type == "namespace" or resource_type == "namespaces":
                resource = self.core_v1.read_namespace(resource_name)
            elif resource_type == "persistentvolume" or resource_type == "persistentvolumes":
                resource = self.core_v1.read_persistent_volume(resource_name)
            elif resource_type == "persistentvolumeclaim" or resource_type == "persistentvolumeclaims":
                resource = self.core_v1.read_namespaced_persistent_volume_claim(
                    resource_name, namespace)
            elif resource_type == "pod" or resource_type == "pods":
                resource = self.core_v1.read_namespaced_pod(
                    resource_name, namespace)
            elif resource_type == "secret" or resource_type == "secrets":
                resource = self.core_v1.read_namespaced_secret(
                    resource_name, namespace)
            elif resource_type == "serviceaccount" or resource_type == "serviceaccounts":
                resource = self.core_v1.read_namespaced_service_account(
                    resource_name, namespace)
            elif resource_type == "service" or resource_type == "services":
                resource = self.core_v1.read_namespaced_service(
                    resource_name, namespace)
            elif resource_type == "node" or resource_type == "nodes":
                resource = self.core_v1.read_node(resource_name)
            elif resource_type == "daemonset" or resource_type == "daemonsets":
                resource = self.apps_v1.read_namespaced_daemon_set(
                    resource_name, namespace)
            elif resource_type == "deployment" or resource_type == "deployments":
                resource = self.apps_v1.read_namespaced_deployment(
                    resource_name, namespace)
            elif resource_type == "replicaset" or resource_type == "replicasets":
                resource = self.apps_v1.read_namespaced_replica_set(
                    resource_name, namespace)
            elif resource_type == "statefulset" or resource_type == "statefulsets":
                resource = self.apps_v1.read_namespaced_stateful_set(
                    resource_name, namespace)
            elif resource_type == "job" or resource_type == "jobs":
                resource = self.batch_v1.read_namespaced_job(
                    resource_name, namespace)
            elif resource_type == "cronjob" or resource_type == "cronjobs":
                resource = self.batch_v1.read_namespaced_cron_job(
                    resource_name, namespace)
            elif resource_type == "ingress" or resource_type == "ingresses":
                resource = self.networking_v1.read_namespaced_ingress(
                    resource_name, namespace)
            elif resource_type == "clusterrole" or resource_type == "clusterroles":
                resource = self.rbac_v1.read_cluster_role(resource_name)
            elif resource_type == "clusterrolebinding" or resource_type == "clusterrolebindings":
                resource = self.rbac_v1.read_cluster_role_binding(
                    resource_name)
            elif resource_type == "role" or resource_type == "roles":
                resource = self.rbac_v1.read_namespaced_role(
                    resource_name, namespace)
            elif resource_type == "rolebinding" or resource_type == "rolebindings":
                resource = self.rbac_v1.read_namespaced_role_binding(
                    resource_name, namespace)
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
        yaml_src = "\n".join(
            [line for line in yaml_src.splitlines() if "null" not in line or "-" in line])
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
    
class KubernetesGetPodNameLikeTool(BaseTool):
    """Tool for getting a pod with a name like the input."""
    name = "k8s_get_pod_name_like"
    description = """
    You should know the namespace and pod name before calling this tool.
    Executes a get in the specified namespace for the specified pod, with the specified name.
    Input should be a string containing the namespace and pod name, separated by commas.
    Returns a yaml string containing the spec.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        namespace, pod_name = tool_input.split(",")
        # remove spaces
        pod_name = pod_name.replace(" ", "")
        resources = self.model.get_resource_list(namespace, "pods")
        resource_names = ",".join([i.metadata.name for i in resources])

        for name in resource_names.split(","):
            if name.startswith(pod_name):
                return name
        return "No pod found with name like: " + pod_name

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)

class KubernetesGetPodLogsTool(BaseTool):
    """Tool for getting the logs of a pod."""
    name = "k8s_get_pod_logs"
    description = """
    You should call the k8s_get_pod_name_like tool first to get the name of the pod.
    You should know the namespace and pod name before calling this tool.
    Executes a get in the specified namespace for the specified pod, with the specified name.
    Input should be a string containing the namespace and pod name, separated by commas.
    Returns a yaml string containing the spec.
    """
    model: KubernetesOpsModel

    def _run(self, tool_input: str) -> str:
        """Run the tool."""
        namespace, pod_name = tool_input.split(",")
        resources = self.model.get_resource_list(namespace, "pods")
        resource_names = self.model.get_running_pod_names(resources)
        # remove spaces
        pod_name = pod_name.replace(" ", "")
        for name in resource_names.split(","):
            if name.startswith(pod_name):
                pod_name = name
            else:
                return "No pod found with name like: " + pod_name
        return self.model.get_logs(namespace, pod_name)

    async def _arun(self, tool_input: str) -> str:
        """Run the tool."""
        return self._run(tool_input)