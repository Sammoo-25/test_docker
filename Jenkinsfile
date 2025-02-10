pipeline {
    agent any

    environment {
        ECR_REPO = 'jenkins-server'
        CONTAINER_NAME = 'weather-container'
        ECR_REPO_URL = '183295448322.dkr.ecr.us-east-1.amazonaws.com/gitlab-test'
        // AWS credentials will be handled within stages
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        url: 'git@github.com:Sammoo-25/test_docker.git',
                        credentialsId: 'github-jenkins-key'
                    ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Initialize SHORT_COMMIT and BUILD_TAG within the script block
                    def shortCommit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def buildTag = "build-${env.BUILD_NUMBER}-${shortCommit}"
                    def dockerImage = "${ECR_REPO_URL}:${buildTag}"

                    echo "Building Docker image with tag: ${dockerImage}"
                    sh "docker build -t ${dockerImage} ."
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'AWS_ACCOUNT_ID', variable: 'AWS_ACCOUNT_ID'),
                        string(credentialsId: 'AWS_REGION', variable: 'AWS_REGION')
                    ]) {
                        def dockerImage = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${buildTag}"
                        echo "Pushing Docker image to AWS ECR: ${dockerImage}"
                        sh """
                            echo "Logging into AWS ECR..."
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                            docker push ${dockerImage}
                        """
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DEPLOYMENT_EC2_IP', variable: 'DEPLOYMENT_EC2_IP'),
                        sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'EC2_SSH_KEY'),
                        string(credentialsId: 'AWS_ACCOUNT_ID', variable: 'AWS_ACCOUNT_ID'),
                        string(credentialsId: 'AWS_REGION', variable: 'AWS_REGION')
                    ]) {
                        def dockerImage = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${buildTag}"
                        echo "Deploying application to EC2 instance: ${DEPLOYMENT_EC2_IP}"
                        sh """
                            ssh -o StrictHostKeyChecking=no -i ${EC2_SSH_KEY} ec2-user@${DEPLOYMENT_EC2_IP} << 'EOF'
                                set -e
                                echo "Logging into AWS ECR..."
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

                                echo "Stopping existing container..."
                                docker stop ${CONTAINER_NAME} || true
                                docker rm ${CONTAINER_NAME} || true

                                echo "Pulling latest image: ${dockerImage}"
                                docker pull ${dockerImage}

                                echo "Running new container..."
                                docker run -d --name ${CONTAINER_NAME} -p 80:8081 ${dockerImage}

                                echo "Deployment successful!"
                            EOF
                        """
                    }
                }
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
