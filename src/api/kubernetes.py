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

def check_readiness():
    load_kubernetes_config()
    v1 = client.CoreV1Api()
    v1.list_namespace()
    return {"status": "ready"}

def get_kubernetes_deployments(label_selector: str):
    load_kubernetes_config()
    v1 = client.AppsV1Api()

    # Use an environment variable for the namespace
    namespace = os.getenv('KUBE_NAMESPACE', 'wod')

    try:
        deployments = v1.list_namespaced_deployment(namespace, label_selector=label_selector)
        return [deployment.metadata.name for deployment in deployments.items]
    except ApiException as e:
        logging.error(f"Error listing deployments: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))

def scale_deployment(label_selector: str, desired_replicas: int):
    load_kubernetes_config()
    v1 = client.AppsV1Api()
    namespace = os.getenv('KUBE_NAMESPACE', 'default')

    try:
        # Find deployments that match the label selector
        deployments = v1.list_namespaced_deployment(namespace, label_selector=label_selector).items
        if not deployments:
            return {"status": "no deployments found with the provided label selector"}

        for deployment in deployments:
            # Get current replica count
            current_replicas = deployment.spec.replicas

            # Check if scaling is necessary
            if current_replicas == desired_replicas:
                continue  # Skip to the next deployment if no scaling is needed

            # Scale the deployment
            deployment.spec.replicas = desired_replicas
            v1.replace_namespaced_deployment(name=deployment.metadata.name, namespace=namespace, body=deployment)

        return {"status": "success updated"}
    except ApiException as e:
        logging.error(f"Error scaling deployment: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))