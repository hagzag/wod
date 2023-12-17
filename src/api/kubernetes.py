from kubernetes import client, config
from kubernetes.client.rest import ApiException
from fastapi import HTTPException
import os
import logging

def load_kubernetes_config():
    try:
        if os.getenv('KUBECONFIG'):
            # Outside Kubernetes cluster
            config.load_kube_config()
        else:
            # Inside Kubernetes cluster
            config.load_incluster_config()
    except Exception as e:
        logging.error(f"Error loading Kubernetes config: {e}")
        raise

def get_kubernetes_deployments(label_selector: str):
    load_kubernetes_config()
    v1 = client.AppsV1Api()

    # Use an environment variable for the namespace
    namespace = os.getenv('KUBE_NAMESPACE', 'default')

    try:
        deployments = v1.list_namespaced_deployment(namespace, label_selector=label_selector)
        return [deployment.metadata.name for deployment in deployments.items]
    except ApiException as e:
        logging.error(f"Error listing deployments: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    
def check_readiness():
    load_kubernetes_config()
    v1 = client.CoreV1Api()
    v1.list_namespace()
    return {"status": "ready"}

def scale_deployment(label_selector: str, desired_replicas: int):
# def scale_deployment(deployment_id, replicas):
    load_kubernetes_config()
    v1 = client.AppsV1Api()
    namespace = config.list_kube_config_contexts()[1]['context']['namespace']
    
    # Get current deployment status
    current_deployment = v1.read_namespaced_deployment(deployment_id, namespace)
    current_replicas = current_deployment.spec.replicas

    # Check if scaling is necessary
    if current_replicas == replicas:
        return {"status": "success unchanged"}

    # Scale the deployment
    body = {'spec': {'replicas': replicas}}
    v1.patch_namespaced_deployment_scale(deployment_id, namespace, body)
    return {"status": "success updated"}