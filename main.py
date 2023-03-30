import base64
import json
import os
from langchain.agents import create_openapi_agent
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.llms.openai import OpenAI
from langchain.requests import RequestsWrapper
from langchain.tools.json.tool import JsonSpec
import googleapiclient.discovery
from tempfile import NamedTemporaryFile
from kubernetes import  client
from agent.base import create_kubernetes_agent
from agent.toolkit import K8sOperationsToolkit

from tools.k8s_operations.tool import KubernetesOpsModel

llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=1024)


def token(*scopes):
    credentials = googleapiclient._auth.default_credentials()
    scopes = [f'https://www.googleapis.com/auth/{s}' for s in scopes]
    scoped = googleapiclient._auth.with_scopes(credentials, scopes)
    googleapiclient._auth.refresh_credentials(scoped)
    return scoped.token

def kubernetes_api(cluster):
    config = client.Configuration()
    config.host = f'https://{cluster["endpoint"]}'

    config.api_key_prefix['authorization'] = 'Bearer'
    config.api_key['authorization'] = token('cloud-platform')

    with NamedTemporaryFile(delete=False) as cert:
        cert.write(base64.decodebytes(cluster['masterAuth']['clusterCaCertificate'].encode()))
        config.ssl_ca_cert = cert.name

    api = client.ApiClient(configuration=config)

    return api

def get_cluster():
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    zone = os.getenv("GOOGLE_REGION")
    cluster_id = os.getenv("GOOGLE_CLUSTER_ID")

    credentials = googleapiclient._auth.default_credentials()
    service = googleapiclient.discovery.build('container', 'v1', credentials=credentials)
    cluster = service.projects().locations().clusters().get(name=f'projects/{project_id}/locations/{zone}/clusters/{cluster_id}').execute()
    return cluster


model = KubernetesOpsModel.from_k8s_client(k8s_client=kubernetes_api(get_cluster()))
toolkit = K8sOperationsToolkit(model=model)
k8s_agent = create_kubernetes_agent(llm=llm, toolkit=toolkit,  verbose=True)


k8s_agent.run("list all namespaces")
k8s_agent.run("list all services in the test-bed namespace")
k8s_agent.run("get the gitlab runner deployment in the gitlab-runner namespace")
k8s_agent.run("get the logs for the review-3 pod in test-bed")

