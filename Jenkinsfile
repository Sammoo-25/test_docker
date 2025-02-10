pipeline {
    agent any

    environment {
        // Use Jenkins credentials for AWS and deployment details
        AWS_ACCOUNT_ID = credentials('AWS_ACCOUNT_ID')
        AWS_REGION = credentials('AWS_REGION')
        ECR_REPO = 'jenkins-server'
        DEPLOYMENT_EC2_IP = credentials('DEPLOYMENT_EC2_IP')
        CONTAINER_NAME = 'weather-container'

        // GitHub SSH credentials for pulling code
        GITHUB_SSH_KEY = credentials('github-jenkins-key')

        // EC2 SSH private key for deployment
        EC2_SSH_KEY = credentials('ec2-ssh-key')

        // Generate dynamic Docker image tag
        SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        BUILD_TAG = "build-${env.BUILD_NUMBER}-${SHORT_COMMIT}"
        DOCKER_IMAGE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${BUILD_TAG}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                sh 'ssh-keyscan github.com >> ~/.ssh/known_hosts'  // Add GitHub's SSH key to known hosts
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        url: 'https://github.com/Sammoo-25/test_docker.git',
                        credentialsId: 'github-jenkins-key'
                    ]]
                ])
            }
        }

        stage('Install Python Dependencies') {
            steps {
                echo 'Installing Python testing tools (flake8, unittest, etc.)...'
                sh '''
                    python -m ensurepip --upgrade
                    python -m pip install --upgrade pip
                    pip install flake8 trivy
                '''
            }
        }

        stage('Linting') {
            steps {
                echo 'Running code linting...'
                sh 'flake8 . || echo "Lint warnings, check output"'
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh 'python -m unittest discover -s tests || exit 1'
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Scanning Docker image for vulnerabilities...'
                sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ${DOCKER_IMAGE} || echo 'Check vulnerabilities manually!'"
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image with tag: ${DOCKER_IMAGE}"
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }

        stage('Push to ECR') {
            steps {
                echo "Pushing Docker image to AWS ECR: ${DOCKER_IMAGE}"
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    docker push ${DOCKER_IMAGE}
                """
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "Deploying application to EC2 instance: ${DEPLOYMENT_EC2_IP}"

                // Add EC2's SSH key to known hosts
                sh 'ssh-keyscan ${DEPLOYMENT_EC2_IP} >> ~/.ssh/known_hosts'

                sh """
                    ssh -o StrictHostKeyChecking=no -i ${EC2_SSH_KEY} ec2-user@${DEPLOYMENT_EC2_IP} << 'EOF'
                        set -e
                        echo "Logging into AWS ECR..."
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

                        echo "Stopping existing container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true

                        echo "Pulling latest image: ${DOCKER_IMAGE}"
                        docker pull ${DOCKER_IMAGE}

                        echo "Running new container..."
                        docker run -d --name ${CONTAINER_NAME} -p 80:8081 ${DOCKER_IMAGE}

                        echo "Deployment successful!"
                    EOF
                """
            }
        }
    }

    post {
        success {
            echo 'Pipeline execution successful!'
        }
        failure {
            echo 'Pipeline execution failed!'
        }
    }
}
