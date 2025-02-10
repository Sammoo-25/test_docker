pipeline {
    agent any

    environment {
        ECR_REPO = 'jenkins-server'
        CONTAINER_NAME = 'weather-container'
        SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        BUILD_TAG = "build-${env.BUILD_NUMBER}-${SHORT_COMMIT}"
        
        // Use Jenkins credentials for AWS and deployment details
        AWS_ACCOUNT_ID = credentials('AVR_ACCOUNT_ID') // Corrected credential ID
        AWS_REGION = credentials('AVR_REGION') // Corrected credential ID
        DEPLOYMENT_EC2_IP = credentials('DEPLOYMENT_EC2_IP') // Corrected credential ID
        
        // Generate dynamic Docker image tag
        DOCKER_IMAGE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${BUILD_TAG}"
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
                        credentialsId: 'github-jenkins-key' // Use the correct credential ID
                    ]]
                ])
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
                withCredentials([
                    string(credentialsId: 'AVR_ACCOUNT_ID', variable: 'AWS_ACCOUNT_ID'),
                    string(credentialsId: 'AVR_REGION', variable: 'AWS_REGION')
                ]) {
                    sh '''
                        echo "Logging into AWS ECR..."
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                        docker push ${DOCKER_IMAGE}
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "Deploying application to EC2 instance: ${DEPLOYMENT_EC2_IP}"
                withCredentials([
                    string(credentialsId: 'DEPLOYMENT_EC2_IP', variable: 'DEPLOYMENT_EC2_IP'),
                    sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'EC2_SSH_KEY')
                ]) {
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