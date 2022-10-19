# Kubernetes

https://d33wubrfki0l68.cloudfront.net/2475489eaf20163ec0f54ddc1d92aa8d4c87c96b/e7c81/images/docs/components-of-kubernetes.svg
https://cdn.buttercms.com/WgQVCgH0TyqCip2ONiSh
https://miro.medium.com/max/1400/0*c2N7STjiWZjCy8we.png

# Swarm

https://miro.medium.com/max/1838/1*dvIZd0ZN-KcjaDDAKTWcLA.png

# Virtualbox

https://www.virtualbox.org/wiki/Downloads

# Chocolatey

https://chocolatey.org/install

# Minikube

https://minikube.sigs.k8s.io/docs/start/
https://minikube.sigs.k8s.io/docs/drivers/virtualbox/
https://minikube.sigs.k8s.io/docs/tutorials/multi_node/

```console
minikube start --driver=virtualbox
minikube start --nodes 2 -p modern-devops --driver=virtualbox
minikube config set driver virtualbox
minikube stop -p modern-devops
minikube start -p modern-devops
```

# Eksctl

https://eksctl.io/
https://eksctl.io/usage/schema/

```console
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl create cluster -f cluster.yaml
aws eks update-kubeconfig --name modern-devops
```

# ECS

https://d2908q01vomqb2.cloudfront.net/fe2ef495a1152561572949784c16bf23abb28057/2020/05/08/image-13.png

# GitOps

