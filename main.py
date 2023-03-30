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
from kubernetes import config, client

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


def get_spec() -> dict:
    cluster = get_cluster()
    api_client = kubernetes_api(cluster)
    return api_client.call_api("/openapi/v2",
                                "GET",
                                path_params={},
                                query_params=[],
                                header_params={},
                                body=None,
                                post_params=[],
                                files={},
                                auth_settings=['BearerToken'],
                                _preload_content=False,
                                _return_http_data_only=True)


# create a json spec from the response
resp = get_spec()
text = resp.data.decode("utf-8")

# write response to file
with open("spec.json", "w") as f:
    f.write(text)
# resp[0] is a json string, so we need to convert it to a dict
json_dict = json.loads(text)


### Remove some stuff from the spec that we don't want to use

# remove the swagger key
json_dict.pop("swagger")

# remove every key under paths that does not begin with '/api/v1'
paths = json_dict["paths"]
for key in list(paths.keys()):
    if not key.startswith("/api/v1"):
        paths.pop(key)


json_spec = JsonSpec(dict_=json_dict, max_value_length=4000)

headers = {
    "Authorization" : f"Bearer {os.getenv('OPENAI_API_KEY')}"
}
requests_wrapper = RequestsWrapper(headers=headers)
openapi_toolkit = OpenAPIToolkit.from_llm(llm=llm, json_spec=json_spec,requests_wrapper=requests_wrapper, verbose=True)
openapi_agent_executor = create_openapi_agent(llm=llm, toolkit=openapi_toolkit, verbose=True)

openapi_agent_executor.run("Get all of the pods from the test-bed namespace.")



