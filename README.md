# Flask CI/CD & Canary Deployment Demo

This project demonstrates a **full DevOps pipeline** for a Python Flask web application, including **CI/CD with Jenkins**, **Docker containerization**, and **Blue-Green / Canary deployment strategies** on **AWS EKS**.  

It showcases real-world DevOps practices suitable for production environments.

---

## Tech Stack

- **AWS EKS & EC2** – Kubernetes cluster and Jenkins host  
- **Jenkins** – CI/CD automation  
- **Docker** – Containerization of Flask app  
- **Python Flask** – Sample web application  
- **GitHub** – Source code repository  
- **Docker Hub** – Container image registry  
- **Kubernetes** – Blue-Green & Canary deployment orchestration  

---

## Repo Structure

01-ci-cd-pipeline/
├── Dockerfile # Flask app container image
├── Jenkinsfile # CI/CD pipeline
├── canary-test.sh # Script to test traffic distribution
├── README.md # This top-level README
└── k8s-manifests/
├── deployment.yaml # Blue deployment
├── deployment-green.yaml # Green/Canary deployment
└── service-lb.yaml # LoadBalancer service

yaml
Copy code

---

## Getting Started

### Prerequisites

- AWS account with **EKS & EC2** access  
- Jenkins installed on EC2 (or local Linux VM)  
- Docker Hub account  
- `kubectl` & `aws-cli` installed and configured  
- GitHub repository with Flask code  

---

## Step 1: Build Docker Image

```bash
docker build -t <dockerhub-username>/flask-cicd-app:latest .
docker push <dockerhub-username>/flask-cicd-app:latest
Step 2: Jenkins CI/CD Pipeline
Open Jenkins → New Item → Pipeline.

Configure pipeline to use Pipeline script from SCM.

Connect to your GitHub repo.

Jenkins will use the Jenkinsfile in the repo:

groovy
Copy code
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<your-username>/devops-portfolio.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t <dockerhub-username>/flask-cicd-app:latest .'
            }
        }
        stage('Push Docker Image') {
            steps {
                withDockerRegistry([credentialsId: 'docker-cred', url: '']) {
                    sh 'docker push <dockerhub-username>/flask-cicd-app:latest'
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f 01-ci-cd-pipeline/k8s-manifests/'
            }
        }
    }
}
Step 3: Deploy Kubernetes Manifests
bash
Copy code
kubectl apply -f k8s-manifests/
This deploys:

Blue app → deployment.yaml

Green app → deployment-green.yaml

Service → service-lb.yaml (LoadBalancer to expose the app)

Step 4: Verify Deployments
bash
Copy code
kubectl get pods
kubectl get svc
kubectl get deployments
Ensure pods are Running.

Note the EXTERNAL-IP / DNS from the service.

Step 5: Test Application
bash
Copy code
curl http://<LOADBALANCER_DNS>/
You should see:

Hello from BLUE version of Flask App
or

Hello from GREEN version of Flask App

Step 6: Blue-Green Deployment
Update app code (app.py) for Green version.

Deploy using deployment-green.yaml.

Service (service-lb.yaml) automatically routes traffic to both deployments.

To switch traffic:

Scale Blue to 0 replicas

Scale Green to desired replicas

bash
Copy code
kubectl scale deployment/flask-deployment --replicas=0
kubectl scale deployment/flask-deployment-green --replicas=3
Step 7: Canary Deployment
Run the canary test script:

bash
Copy code
chmod +x canary-test.sh
./canary-test.sh <LOADBALANCER_DNS> 100
This sends 100 requests and shows how traffic is split between Blue and Green.

Step 8: Adjust Canary Rollout
Start with more Blue replicas, fewer Green replicas:

bash
Copy code
# Example: Blue=4, Green=1 (initial)
kubectl scale deployment/flask-deployment --replicas=4
kubectl scale deployment/flask-deployment-green --replicas=1
Gradually shift traffic by adjusting replicas:

bash
Copy code
kubectl scale deployment/flask-deployment --replicas=3
kubectl scale deployment/flask-deployment-green --replicas=2
Test again with canary-test.sh.

Step 9: Rollback (if needed)
bash
Copy code
# Rollback Green to 0 replicas
kubectl scale deployment/flask-deployment-green --replicas=0

# Or undo deployment
kubectl rollout undo deployment/flask-deployment-green
Notes / Best Practices
Readiness Probes → Ensure pods only get traffic when ready.

Liveness Probes → Restart unhealthy pods automatically.

CI/CD Pipeline → Automates build, push, and deploy steps.

Always keep rollback commands ready during Canary or Blue-Green rollouts.

