pipeline {
    agent any

    environment {
        // Define Docker image name and ECR repository
        DOCKER_IMAGE_NAME = "jenkins-server"
        ECR_REPOSITORY = "183295448322.dkr.ecr.us-east-1.amazonaws.com/jenkins-server"


        DEPLOYMENT_EC2_IP = credentials('DEPLOYMENT_EC2_IP')
        AWS_REGION = credentials('AWS_REGION')
    }

    stages {
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

                    // Tag Docker image
                    sh "docker tag ${DOCKER_IMAGE_NAME}:latest ${ECR_REPOSITORY}:latest"

                    // Push Docker image to ECR
                    sh "docker push ${ECR_REPOSITORY}:latest"
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
                            # Log in to AWS ECR
                            ssh -o StrictHostKeyChecking=no ec2-user@${DEPLOYMENT_EC2_IP} "
                                aws ecr get-login-password --region ${AWS_REGION} | \
                                docker login --username AWS --password-stdin ${ECR_REPOSITORY} &&

                                # Pull the latest Docker image
                                docker pull ${ECR_REPOSITORY}:latest &&

                                # Stop and remove the existing container (if any)
                                docker stop ${DOCKER_IMAGE_NAME} || true &&
                                docker rm ${DOCKER_IMAGE_NAME} || true &&

                                # Run the new container
                                docker run -d --name ${DOCKER_IMAGE_NAME} -p 80:80 ${ECR_REPOSITORY}:latest
                            "
                        """
                    }
                }
            }
        }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}