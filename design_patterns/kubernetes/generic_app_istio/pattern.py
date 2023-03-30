from design_patterns.design_pattern import DesignPattern


class GenericAppWithIstio(DesignPattern):
    name = """Generic Kubernetes App with Istio"""
    use_case = """Use this design pattern when the Kubernetes cluster supports istio and has an istio gateway."""
    description = """The expected values that need to be supplied are:
    - app_name
    - root_domain
    - image
    - port (optional) - default to 8080
    - namespace (optional) - default to app_name
    - istio_gateway (optional) - default to istio-system/istio-ingressgateway
    - istio_gateway_namespace (optional) - default to istio-system
    - secret_name(s) (optional)
    - env_names and env values (optional)
    This design pattern creates manifests for a deployment, service, service account, virtual service, and destination rule.
    The files should be placed in the namespace/app_name directory of the cluster repo.
    """
    template_path = "design_patterns/kubernetes/generic_app_istio/templates"