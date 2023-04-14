# Complete Minecraft Server Deployment (CloudFormation)

The template contained within this repository can be used to deploy a Minecraft server to Amazon Web Services (AWS) in minutes. As the solution leverages "Spot Pricing", the server should cost less than a cent an hour to run, and you can even turn it off when you and your friends aren't playing - saving even more money.

## Prerequisites

A basic understanding of Amazon Web Services, specifically CloudFormation.
An AWS Account.
Basic knowledge of Linux administration (no more than what would be required to just use the itzg/docker-minecraft-server Docker image).

## Overview

The solution is based on the Factorio Spot Pricing template and the itzg/docker-minecraft-server Docker image.

The CloudFormation template launches an ephemeral instance that joins an Elastic Container Service (ECS) cluster. Within this ECS cluster, an ECS service is configured to run a Minecraft Docker image. The ephemeral instance does not store any saves, mods, or Minecraft configuration data; instead, all of this state is stored on a network file system (Elastic File System - EFS).

The template is configured to launch the ephemeral instance using spot pricing, which can save up to 90% on regular "on-demand" pricing in AWS. However, there are some drawbacks: your instance might be terminated if someone else places a higher bid than you in the spot pricing auction.

The solution uses the following AWS services:

- EFS - Elastic File System is used to store Minecraft configuration, save games, mods, etc. None of this data is stored on the server itself, as it may be terminated at any time.
- Auto Scaling - An Auto Scaling Group is used to maintain a single instance via spot pricing.
- VPC - The template deploys a basic VPC for use by the Minecraft server. This does not incur any additional cost.

## Getting Started

1. Click Launch Stack to log into your AWS account and start the CloudFormation deployment process.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=minecraft)

2. Ensure you've selected a suitable AWS region (closest to you) using the selector at the top right.
3. Upload the cf.yml file.
4. Click "Next" to proceed through the CloudFormation deployment, providing parameters on the following page. You'll need a Key Pair and your Public IP address for remote access (recommended). Refer to the "Remote Access" section below. There should be no need to touch any other parameters unless you have a specific reason to do so. Continue through the rest of the deployment.

After the deployment is complete, your Minecraft server should be running within a few minutes. Once the stack status is reported as "CREATE_COMPLETE", go to the EC2 dashboard in the AWS console, and you should see a running Minecraft server. Take note of the public IP address, which can be used to connect to the server using a Minecraft client.

At this point, you should configure remote access as per the "Remote Access" section below, allowing you to modify the server.properties file (e.g., view-distance, allow nether, etc.).

## Optional Features

- Remote Access
  Create a Key Pair (Services > EC2 > Key Pairs). You'll need to use this to connect to the instance for additional setup.
  Find your public IP address. You'll need this to connect to the instance for additional setup.
- Custom Domain Name
  DNS Configuration
  Lambda function fires off and creates / updates the record of your choosing. This way, you can have a custom domain name such as "minecraft.mydomain.com" that points to your Minecraft server.

## FAQ

1. Do I need a VPC, or Subnets, or other networking config in AWS?
   No. The template will create a VPC and Subnets for you. You can use the default VPC if you prefer, but this is not recommended.

2. What if my server is terminated due to my Spot Request being outbid?
   The Auto Scaling Group will automatically launch a new instance to replace the terminated instance. The Minecraft server will be restarted automatically.

3. My server keeps getting terminated. I don't like Spot Pricing. Take me back to the good old days.
   You can change the Auto Scaling Group to use on-demand pricing. This will be more expensive, but you won't have to worry about your server being terminated.

4. How do I change my instance type?
   You can change the instance type in the Auto Scaling Group. The Minecraft server will be restarted automatically.

5. How do I change my spot price limit?
   You can change the spot price limit in the Auto Scaling Group. The Minecraft server will be restarted automatically.

6. How do I change the Minecraft server version?
   You can change the Minecraft server version in the ECS Service. The Minecraft server will be restarted automatically.

7. How can I change map settings, server settings etc.
   You'll need to have remote access to the server (refer to Optional Features). You can make whatever changes you want to the configuration in /opt/minecraft/. Once done, restart the container:

   Go to ECS (Elastic Container Service) in the AWS Console
   Click the minecraft cluster
   Tick the minecraft service, and select update
   Tick "Force new deployment"
   Click Next 3 times, and finally Update service

## Expected Costs

The main components that incur charges are:

- EC2 - The EC2 instance is used to run the Minecraft server. The instance is configured to use spot pricing, which can save up to 90% on regular "on-demand" pricing in AWS. However, there are some drawbacks: yours instance might be terminated if someone else places a higher bid than you in the spot pricing auction. If you're using spot pricing (and the t3.medium instance as per the default in the template), I've been running my server nonstop for a month and the total cost was around $10/mo

- EFS - Elastic File System is used to store Minecraft configuration, save games, mods, etc. None of this data is stored on the server itself, as it may be terminated at any time.Charged per Gigabyte stored per month (GB-Month). Varies based on region, but typically less than 50c per gigabyte. My EFS file system for Minecraft cost 7 cents per month
  AWS do charge for data egress (i.e. data being sent from your Minecraft server to clients), but again this should be barely noticeable.
