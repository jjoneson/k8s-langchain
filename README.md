# A [LangChain Agent](https://github.com/hwchase17/langchain) for interacting with Kubernetes Clusters using Large Language Models

## Requirements

For indexing PDFs:
- poppler

on Mac:
```bash
brew install poppler
```
on Ubuntu:
```bash
sudo apt-get install poppler-utils
```

## Capabilities
  - Connect to a remote GKE Cluster
  - Supports most of core, apps, batch, networking, and rbac API groups
    - Specifically: `configmap, namespace, persistentvolume, persistentvolumeclaim, pod ,secret, serviceaccount, service, node, daemonset, deployment, replicaset, statefulset, job, cronjob, ingress, clusterrole, clusterrolebinding, role, rolebinding`
  - List namespaces
  - List object names by type in a namespace
  - Get a resource by name, type, and namespace (if applicable)
  - Get logs for a pod by name prefix and namespace
  
## Required Env Vars
| Name | Description |
|----------------------------|-----------------------------|
| OPENAI_API_KEY | API Key for OpenAI API |
| OPENAI_ORG_ID | Organization ID for OpenAI API |
| GOOGLE_PROJECT_ID | Project ID for GCP |
| GOOGLE_REGION | Region for GCP |
| GOOGLE_CLUSTER_ID | Cluster Name for GCP |
| SLACK_APP_TOKEN | Slack App Token for Slack API |
| SLACK_BOT_TOKEN | Slack Bot Token for Slack API |
| SLACK_CHANNEL_ID | Slack Channel ID for Slack API |

This assumes that you are running locally and are able to authenticate by running:
```bash
gcloud auth application-default login
```

## Example Output
```python
k8s_agent.run("get the gitlab runner deployment in the gitlab-runner namespace")
```

```yaml
> Entering new AgentExecutor chain...
Action: k8s_get_object_names
Action Input: "gitlab-runner,deployment"
Observation: gitlab-runner
Thought: I should determine the operation I need to perform.
Action: k8s_determine_operations
Action Input: "deployment"
Observation: create,read,list,update,delete
Thought: I need to perform a get operation on the deployment.
Action: k8s_get_resource
Action Input: "gitlab-runner,deployment,gitlab-runner"
Observation: api_version: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: '3'
    meta.helm.sh/release-name: gitlab-runner
    meta.helm.sh/release-namespace: gitlab-runner
  creation_timestamp: 2023-03-06 02:04:43+00:00
  generation: 4
  labels:
    app: gitlab-runner
    app.kubernetes.io/managed-by: Helm
    chart: gitlab-runner-0.50.1
    heritage: Helm
    release: gitlab-runner
  name: gitlab-runner
  namespace: gitlab-runner
spec:
  progress_deadline_seconds: 600
  revision_history_limit: 10
...
```

```python
k8s_agent.run("list all namespaces")
k8s_agent.run("list all services in the test-bed namespace")
```
```yaml
> Entering new AgentExecutor chain...
Action: k8s_get_available_resource_types
Action Input: None
Observation: configmap,namespace,persistentvolume,persistentvolumeclaim,pod,secret,serviceaccount,service,node,daemonset,deployment,replicaset,statefulset,job,cronjob,ingress,clusterrole,clusterrolebinding,role,rolebinding
Thought: I need to list all namespaces, so I should use the k8s_get_available_namespaces tool.
Action: k8s_get_available_namespaces
Action Input: None
Observation: cert-manager,default,gitlab-agent,gitlab-managed-apps,gitlab-runner,gitlab-webhook-dev,kube-node-lease,kube-public,kube-system,test-bed
Thought: I now have a comma separated list of all available namespaces.
Final Answer: cert-manager,default,gitlab-agent,gitlab-managed-apps,gitlab-runner,gitlab-webhook-dev,kube-node-lease,kube-public,kube-system,test-bed

> Finished chain.


> Entering new AgentExecutor chain...
Action: k8s_get_object_names
Action Input: "test-bed,service"
Observation: review-1-initial-hqmue1-auto-deploy,review-3-initial-e0a0ju-auto-deploy,review-3-initial-e0a0ju-postgresql,review-3-initial-e0a0ju-postgresql-headless
Thought: I now know the names of all services in the test-bed namespace.
Final Answer: review-1-initial-hqmue1-auto-deploy,review-3-initial-e0a0ju-auto-deploy,review-3-initial-e0a0ju-postgresql,review-3-initial-e0a0ju-postgresql-headless

> Finished chain.
```

```python
k8s_agent.run("get the logs for review-3 in test-bed")
```
```yaml
> Entering new AgentExecutor chain...
Action: k8s_get_pod_logs
Action Input: test-bed, review-3
Observation: postgresql 21:24:28.14 
postgresql 21:24:28.14 Welcome to the Bitnami postgresql container
postgresql 21:24:28.14 Subscribe to project updates by watching https://github.com/bitnami/bitnami-docker-postgresql
postgresql 21:24:28.15 Submit issues and feature requests at https://github.com/bitnami/bitnami-docker-postgresql/issues
postgresql 21:24:28.15 Send us your feedback at containers@bitnami.com
postgresql 21:24:28.15 
postgresql 21:24:28.17 INFO  ==> ** Starting PostgreSQL setup **
postgresql 21:24:28.25 INFO  ==> Validating settings in POSTGRESQL_* env vars..
postgresql 21:24:28.26 INFO  ==> Loading custom pre-init scripts...
postgresql 21:24:28.26 INFO  ==> Initializing PostgreSQL database...
postgresql 21:24:28.28 INFO  ==> postgresql.conf file not detected. Generating it...
postgresql 21:24:28.29 INFO  ==> pg_hba.conf file not detected. Generating it...
postgresql 21:24:28.29 INFO  ==> Generating local authentication configuration
postgresql 21:24:28.30 INFO  ==> Deploying PostgreSQL with persisted data...
postgresql 21:24:28.31 INFO  ==> Configuring replication parameters
postgresql 21:24:28.33 INFO  ==> Configuring fsync
postgresql 21:24:28.34 INFO  ==> Loading custom scripts...
postgresql 21:24:28.35 INFO  ==> Enabling remote connections
postgresql 21:24:28.36 INFO  ==> Stopping PostgreSQL...
postgresql 21:24:28.37 INFO  ==> ** PostgreSQL setup finished! **

postgresql 21:24:28.43 INFO  ==> ** Starting PostgreSQL **
LOG:  database system was shut down at 2023-03-26 21:21:58 GMT
LOG:  MultiXact member wraparound protections are now enabled
LOG:  database system is ready to accept connections
LOG:  autovacuum launcher started
...
```