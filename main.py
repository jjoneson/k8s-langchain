import base64
import json
import os
import gitlab
from langchain.agents import create_openapi_agent
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.chat_models import ChatOpenAI
from langchain.requests import RequestsWrapper
from langchain.tools.json.tool import JsonSpec
import googleapiclient.discovery
from tempfile import NamedTemporaryFile
from kubernetes import  client
from slack_sdk import WebClient
from agent.factory import AgentFactory
from agent.toolkits.base import create_k8s_engineer_agent
from agent.toolkits.git_integrator.toolkit import GitIntegratorToolkit
from agent.toolkits.k8s_explorer.base import create_k8s_explorer_agent
from agent.toolkits.k8s_explorer.toolkit import K8sExplorerToolkit
from agent.toolkits.toolkit import K8sEngineerToolkit
from listeners.slack_listener import SlackListener
from tools.git_integrator.tool import GitModel
from tools.gitlab_integration.tool import GitlabModel

from tools.k8s_explorer.tool import KubernetesOpsModel
from tools.slack_integration.tool import SlackModel

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=2048)


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


k8s_model = KubernetesOpsModel.from_k8s_client(k8s_client=kubernetes_api(get_cluster()))

git_username = os.getenv("GIT_USERNAME", "k8s-engineer")
git_password = os.getenv("GIT_PASSWORD", "dummy-password")
git_model = GitModel(username=git_username, password=git_password)


gitlab_private_token = os.getenv("GITLAB_PRIVATE_TOKEN", "dummy-token")
gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")

gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_private_token)
gitlab_model = GitlabModel(gl=gl)

slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(token=slack_token)
slack_channel = os.environ["SLACK_CHANNEL_ID"]
slack_model = SlackModel(client=slack_client, channel=slack_channel)

k8s_engineer_toolkit = K8sEngineerToolkit.from_llm(llm=llm, k8s_model=k8s_model, git_model=git_model, gitlab_model=gitlab_model, slack_model=slack_model,  verbose=True)
k8s_engineer_agent = create_k8s_engineer_agent(llm=llm, toolkit=k8s_engineer_toolkit, verbose=True)

slack_listener = SlackListener(AgentFactory())
interrupt = slack_listener.start()
# block until keyboard interrupt
interrupt.wait()


# # k8s_agent.run("list all namespaces")
# # k8s_agent.run("list all services in the test-bed namespace")
# # k8s_agent.run("get the gitlab runner deployment in the gitlab-runner namespace")
# k8s_engineer_agent.run("get the logs for review-3 in test-bed")

