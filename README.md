# wod - worker on demand

## starting local demo

1. git clone this repo
2. task run-api-local

## Use Cases

In a given namespace running the `api` this api can spinup a worker on demand based on an api call

- `/workers/list` - return list of replicas of agiven deploymnet filter by `label_selector` same as running `kubectl -n wod get deploy -l unique-instance-id=worker-0`
- `/worker/activate` - scale a deployment from `0` to `1`
- `/worker/deactivate` - scale a deployment from `1` to `0`

### get replica count

The equivalent of kubectl -n wod get deploy -l unique-instance-id=worker-0 

```sh
curl -X GET http://localhost:9090/workers/list?label_selector=unique-instance-id=worker-0
```

### scale-up replicas from 0 to 1

The equivalent of kubectl -n wod scale deploy -l unique-instance-id=worker-0 --replicas 1

```sh
curl -X POST http://localhost:9090/worker/activate?label_selector=unique-instance-id=worker-0
```

### scale-down replicas from 1 to 0

The equivalent of kubectl -n wod scale deploy -l unique-instance-id=worker-0 --replicas 1

```sh
curl -X POST http://localhost:9090/worker/deactivate?label_selector=unique-instance-id=worker-0
```

## Deploy to kubernetes

using Playground cluster:

```sh
aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION --profile $AWS_PROFILE
```

### using kustomize

```sh
k apply -k .kustomize/
namespace/wod unchanged
serviceaccount/deployment-manager-sa unchanged
role.rbac.authorization.k8s.io/deployment-manager unchanged
clusterrole.rbac.authorization.k8s.io/namespace-listener unchanged
rolebinding.rbac.authorization.k8s.io/deployment-manager-binding unchanged
clusterrolebinding.rbac.authorization.k8s.io/namespace-listener-binding unchanged
service/api unchanged
deployment.apps/api unchanged
deployment.apps/worker unchanged
```

