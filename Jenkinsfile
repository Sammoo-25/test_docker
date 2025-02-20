pipeline {
    agent any

    environment {
        // Define Docker image name and ECR repository
        DOCKER_IMAGE_NAME = "jenkins-server"
        ECR_REPOSITORY = "183295448322.dkr.ecr.us-east-1.amazonaws.com/jenkins-server"

        // Define deployment EC2 IP and AWS region
        DEPLOYMENT_EC2_IP = credentials('DEPLOYMENT_EC2_IP')
        AWS_REGION = credentials('AWS_REGION')
    }

    stages {
        stage('Set Image Tag') {
            steps {
                script {
                    // Define dynamic Docker tag using Jenkins build number
                    env.IMAGE_TAG = "latest-${BUILD_NUMBER}"
                    echo "Docker image tag set to: ${env.IMAGE_TAG}"
                }
            }
        }

        // Stage 1: Clone the repository from GitHub
        stage('Clone Repository') {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']], // Replace with your branch name
                        extensions: [],
                        userRemoteConfigs: [[
                            url: 'https://github.com/Sammoo-25/test_docker.git', // Replace with your GitHub repo URL
                            credentialsId: 'github-jenkins-key'
                        ]]
                    ])
                }
            }
        }

        // Stage 2: Build Docker image and push to AWS ECR
        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Log in to AWS ECR
                    withCredentials([string(credentialsId: 'AWS_ACCOUNT_ID', variable: 'AWS_ACCOUNT_ID'),
                                    string(credentialsId: 'AWS_REGION', variable: 'AWS_REGION')]) {
                        sh """
                            aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ECR_REPOSITORY}
                        """
                    }

                    // Build Docker image
                    sh "docker build -t ${DOCKER_IMAGE_NAME} ."

                    // Tag Docker image with dynamic IMAGE_TAG
                    sh "docker tag ${DOCKER_IMAGE_NAME} ${ECR_REPOSITORY}:${env.IMAGE_TAG}"

                    // Push Docker image to ECR
                    sh "docker push ${ECR_REPOSITORY}:${env.IMAGE_TAG}"
                }
            }
        }

        // Stage 3: Deploy to target EC2 instance
        stage('Deploy to EC2') {
            steps {
                script {
                    // SSH into the target EC2 instance and run commands
                    sshagent(['ec2-ssh-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ec2-user@${DEPLOYMENT_EC2_IP} "
                                # Log in to AWS ECR
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY} &&

                                # Pull the latest Docker image
                                docker pull ${ECR_REPOSITORY}:${env.IMAGE_TAG} &&

                                # Stop and remove the existing container (if any)
                                docker stop ${DOCKER_IMAGE_NAME} || true &&
                                docker rm ${DOCKER_IMAGE_NAME} || true &&

                                # Run the new container
                                docker run -d --name ${DOCKER_IMAGE_NAME} -p 8081:8081 ${ECR_REPOSITORY}:${env.IMAGE_TAG}
                            "
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!!!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}