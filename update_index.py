import os
from doc_indexes.k8s_index import KubernetesIndex

k8s_doc_url = os.getenv("K8S_DOC_URL", "https://github.com/dohsimpson/kubernetes-doc-pdf/raw/master/PDFs/Reference.pdf")
k8s_index = KubernetesIndex(doc_url=k8s_doc_url)
k8s_index.update_index()