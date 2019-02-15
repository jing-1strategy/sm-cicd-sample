# Create a Pipeline with an Github Enterprise Source and Deploy to ECS-Fargate
This is a sample project shows you how to create a complete, end-to-end continuous integration and continuous deployment (CICD) pipeline with AWS CodePipeline. It walks you through setting up a pipeline to build and deploy your application when code is updated in github enterprise.

# Running the Sample

## Prerequisites:

1. Generate a personal access token for your CodeBuild project.  
    * In Github enterprise > Settings > Developer settings > Personal access tokens > [Generate new token].
    * When you create the personal access token, include the "repo" scope in the definition.
    * Copy it to your clipboard so that it can be used when you create your CodeBuild project.

1. Download your certificate from GitHub Enterprise. CodeBuild uses the certificate to make a trusted SSL connection to the repository.
    * From a terminal window, run the following command:

      ```
      echo -n | openssl s_client -connect code.corp.surveymonkey.com:443 \
    | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/githubcert.pem
      ```
1. Upload your certificate file to an Amazon S3 bucket which in the same AWS region as your builds.

## Step 1: Create a Build Project with GitHub Enterprise as the Source Repository and Enable Webhooks

1. Create an image repository in Amazon ECR named "cicd-demo" and update buildspec.yml with push commands to this repo.

1. Create CodeBuild Project with below settings:
    * Source provider: GitHub Enterprise
    * Personal Access Token: paste the token you copied to your clipboard and choose Save Token
    * Repository URL: https://code.corp.surveymonkey.com/jingliang/cicd-source
    * Select Rebuild every time a code change is pushed to this repository
    * Select Enable insecure SSL to ignore SSL warnings  (for testing only, not production)
    * Environment: 
        * choose Managed image
        * Operating system: Ubuntu
        * Runtime: Docker
        * Runtime version: aws/codebuild/docker:18.09.0
    * Service Role:
        * Select [New service role]
        * Role name: accept the defaut name.
    * Buildspec
        * Use a buildspec file. By default, CodeBuild looks for a file named buildspec.yml in the source code root directory.

1. Create a webhook for your GitHub Enterprise repository
    * Create webhook dialog box is displayed with values for Payload URL and Secret. The Create webhook dialog box appears only once. Copy the payload URL and secret key. You need them when you add a webhook in GitHub Enterprise.
    * In GitHub Enterprise, choose the repository where your CodeBuild project is stored.
    * Choose Settings, choose Hooks, and then choose Add webhook.
    * Enter the payload URL and secret key, accept the defaults for the other fields, and then choose Add webhook.

1. Add below policy to the CodeBuild service role:

    ```json
    {
    "Statement": [
        {
        "Action": [
            "ecr:BatchCheckLayerAvailability",
            "ecr:CompleteLayerUpload",
            "ecr:GetAuthorizationToken",
            "ecr:InitiateLayerUpload",
            "ecr:PutImage",
            "ecr:UploadLayerPart"
        ],
        "Resource": "*",
        "Effect": "Allow"
        },
    ],
    "Version": "2012-10-17"
    }

    ```
1. Click Start build

## Step 2: Create CodeDeploy Application and Deployment Group (Fargate Compute Platform)

1. Update a task definition JSON file and register it with Amazon ECS

    * Create ecsTaskExecutionRole with AmazonECSTaskExecutionRolePolicy

    * Update Task Definition Source File (taskdef.json) with ecsTaskExecutionRole arn and ECR image name

    * Register your task definition with the taskdef.json file.

    ```bash
    aws ecs register-task-definition --cli-input-json file://taskdef.json
    ```

    * After the task definition is registered, edit your file to remove the image name and include the <IMAGE1_NAME> placeholder text in the image field.

    * Note: In appspec.yaml, for TaskDefinition, do not change the <TASK_DEFINITION> placeholder text. This value is updated when your pipeline runs.

1.  Create Application Load Balancer and Target Groups

    * Create Application Load Balancer with below settings:
        * Scheme: internet-facing.
        * Configure two listener ports for your load balancer:
            * Under Load Balancer Protocol, choose HTTP. Under Load Balancer Port, enter 80
            * Choose Add listener
            * Under Load Balancer Protocol for the second listener, choose HTTP. Under Load Balancer Port, enter 8080.
            * In Target group, choose New target group and configure your first target group:
                * In Name, enter a target group name (for example, cicd-demo-tg-1)
                * In Target type, choose IP
                * In Protocol choose HTTP. In Port, enter 80
            * Create a second target group for your load balancer
                * In Name, enter a target group name (for example, cicd-demo-tg-2)
                * In Target type, choose IP
                * In Protocol choose HTTP. In Port, enter 8080
            * Update your load balancer to include your second target group

1. Create Your Amazon ECS Fargate Cluster and Service
    * Create a ECS Fargate Cluster named CICD-DEMO
    * Update create-service.json and run the create-service command:

    ```bash
    aws ecs create-service --service-name cicd-demo-service --cli-input-json file://create-service.json
    ```
1. Create CodeDeploy Application and Deployment Group
    * Create an CodeDeploy application with below settings:
        * Application name: CICD-CodeDeploy-Application
        * Compute platform: Amazon ECS

    * Create an CodeDeploy deployment group with below settings:
        * Deployment group name: CICDDemo-DeploymentGroup
        * Service Role: choose AWSCodeDeployRoleForECS (with AWS managed policy AWSCodeDeployRoleForECS)
        * ECS cluster name: CICD-DEMO
        * Choose an ECS service name: cicd-demo-service
        * Load balancer: cicd-demo-alb
        * Production listener port: HTTP: 80
        * Test listener port : HTTP:8080
        * Target group 1 name: cicd-demo-tg-1
        * Target group 2 name: cicd-demo-tg-2
        * Deployment settings: Reroute traffic immediately

## Step 3: Create Code Pipeline

1. Choose pipeline settings
    * enter pipeline name as use default settings for other fields

1. Add source stage
    * Source provider: GitHub
    * Grant AWS CodePipeline access to your GitHub repository
    * Repository: jing-1strategy/sm-cicd-sample
    * Branch: master
    * Change detection options: GitHub webhooks

1. Add build stage
    * Build provider: AWS CodeBuild
    * Project name: CICD-CodeBuild-Project

1. Add deploy stage
    * Deploy provider: AWS CodeDeploy
    * Application name: CICD-CodeDeploy-Application
    * Deployment group: CICD-DeploymentGroup

1. Review and Create Pipeline.