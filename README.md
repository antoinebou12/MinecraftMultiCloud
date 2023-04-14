# Minecraft Multi-Cloud Infrastructure

## Overview

The Minecraft Multi-Cloud Infrastructure project aims to deploy a Minecraft server across multiple cloud providers using Infrastructure as Code (IaC) tools like Terraform and Pulumi. By leveraging these tools, we can create, manage, and scale the server infrastructure seamlessly, providing a consistent experience across different cloud platforms.

## Features

- Scalable Minecraft server infrastructure
- Multi-cloud deployment across major cloud providers (AWS, Azure, Google Cloud, etc.)
- Automated infrastructure management using Terraform and Pulumi
- High availability and fault tolerance
- Automated backups and recovery
- Monitoring and logging capabilities
- Prerequisites
- Before you can use this project, ensure that you have the following installed on your local machine:
- Terraform (version 1.0.0 or later)
- Pulumi (version 3.0.0 or later)
- Python (version 3.6 or later)

Additionally, you need to have access to the following cloud platforms:

- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCP)
- Local machine

Ensure that you have valid API keys and/or authentication credentials for each platform.

Getting Started
Clone the repository:

```
git clone https://github.com/antoinebou12/MinecraftMultiCloud.git
cd MinecraftMultiCloud
```

Initialize Terraform and Pulumi:

```
terraform init
pulumi init
```

Configure the cloud provider credentials by setting the appropriate environment variables. For example:

```
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AZURE_CLIENT_ID=your_client_id
export AZURE_CLIENT_SECRET=your_client_secret
export AZURE_TENANT_ID=your_tenant_id
export GOOGLE_APPLICATION_CREDENTIALS=path_to_your_gcp_credentials_file
```

Configure the variables.tf and Pulumi.yaml files with the appropriate values for your deployment.

Run the following commands to deploy the infrastructure:

```
terraform apply
pulumi up
```

After the deployment is complete, you will receive the public IP addresses for your Minecraft servers. Connect to the server using a Minecraft client to start playing.

Cleaning Up
To destroy the infrastructure and clean up the resources, run the following commands:

```
terraform destroy
pulumi destroy
```

Contributing
Please feel free to submit issues, fork the repository, and send pull requests to contribute to the project.

License
This project is licensed under the MIT License - see the LICENSE file for details.
