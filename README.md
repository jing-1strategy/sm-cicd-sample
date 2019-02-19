# Create a Pipeline with an Github Source and Deploy to ECS-Fargate
This is a sample project shows you how to create a complete, end-to-end continuous integration and continuous deployment (CICD) pipeline with AWS CodePipeline. It walks you through setting up a pipeline to build and deploy your application when code is updated in github.

# Running the Sample

## Prerequisites:

1. Generate a personal access token for your CodeBuild project.  
    * In Github > Settings > Developer settings > Personal access tokens > [Generate new token].
    * When you create the personal access token, include the "repo" scope in the definition:
        * repo: Grants full control of private repositories.
        * repo:status: Grants access to commit statuses.
        * admin:repo_hook: Grants full control of repository hooks. This scope is not required if your token has the repo scope.
    * Copy it to your clipboard so that it can be used when you create your CodeBuild project.
1. Create an image repository in Amazon ECR named "cicd-demo" and update buildspec.yml with push commands to this repo.

## Step 1: Create a CodeBuild Project for Unit Test

1. Create CodeBuild Project with below settings: (e.g. CICD-CodeBuild-UnitTest)
    * Source provider: GitHub
    * Repository: Connect with a GitHub personal access token.
    * Github personal access token: paste the token you copied to your clipboard and choose Save Token
    * Repository URL: https://github.com/jing-1strategy/sm-cicd-sample
    * Select Rebuild every time a code change is pushed to this repository
    * Event type: PUSH (or others depends on the requirement)
    * Environment:
        * choose Managed image
        * Operating system: Ubuntu
        * Runtime: Python
        * Runtime version: aws/codebuild/python:3.7.1
    * Service Role:
        * Select [New service role]
        * Role name: accept the default name.
    * Buildspec
        * Use a buildspec file.
        * Buildspec name: buildspec-unit-test.yml

## Step 2: Create a CodeBuild Project for push docker image to ECR

1. Create CodeBuild Project with below settings: (e.g. CICD-CodeBuild-Image)

    * Source provider: GitHub
    * Github repository: jing-1strategy/sm-cicd-sample
    * Select Rebuild every time a code change is pushed to this repository
    * Event type: PUSH (or others depends on the requirement)
    * Environment:
        * choose Managed image
        * Operating system: Ubuntu
        * Runtime: Docker
        * Runtime version: aws/codebuild/docker:18.09.0
    * Service Role:
        * Select [New service role]
        * Role name: accept the default name.
    * Buildspec
        * Use a buildspec file.
        * Buildspec name: buildspec-image.yml

1. Add below policy to the CodeBuild service role to allow pushing image to ECR:

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

## Step 3: Create CodeDeploy Application and Deployment Group (Fargate Compute Platform)

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

## Step 4: Create a CodeCommit Repository and push appspec.yaml and taskdef.json to it

1. Create a CodeCommit repository: e.g.SM-Github-CICD-Pipeline
1. Push appspec.yaml and taskdef.json to your CodeCommit repository.

## Step 5: Create Continuous Integration Pipeline

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
    * Deploy provider: Amazon ECS (Blue/Green)
    * AWS CodeDeploy application name: CICD-CodeDeploy-Application
    * AWS CodeDeploy deployment group: CICD-DeploymentGroup

1. Review and Create Pipeline.

Test: update something.