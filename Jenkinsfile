pipeline {
    agent any

    environment {
        // Retrieve credentials from Jenkins
        AWS_ACCOUNT_ID = credentials('AWS_ACCOUNT_ID')
        AWS_REGION = credentials('AWS_REGION')
        DEPLOYMENT_EC2_IP = credentials('DEPLOYMENT_EC2_IP')
        GITHUB_SSH_KEY = credentials('github-jenkins-key')
        EC2_SSH_KEY = credentials('ec2-ssh-key')
        
        // Define Docker image name and ECR repository
        DOCKER_IMAGE_NAME = "weather-app"
        ECR_REPOSITORY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${DOCKER_IMAGE_NAME}"
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
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    """

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
                            ssh -o StrictHostKeyChecking=no ec2-user@${DEPLOYMENT_EC2_IP} << 'EOF'
                            # Log in to AWS ECR
                            aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

                            # Pull the latest Docker image
                            docker pull ${ECR_REPOSITORY}:latest

                            # Stop and remove the existing container (if any)
                            docker stop ${DOCKER_IMAGE_NAME} || true
                            docker rm ${DOCKER_IMAGE_NAME} || true

                            # Run the new container
                            docker run -d --name ${DOCKER_IMAGE_NAME} -p 80:80 ${ECR_REPOSITORY}:latest
                            EOF
                        """
                    }
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