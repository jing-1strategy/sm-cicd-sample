# Create a Pipeline with an Github Enterprise Source and ECS-to-CodeDeploy Deployment
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

