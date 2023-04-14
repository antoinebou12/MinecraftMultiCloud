import json

import pulumi_aws as aws

import pulumi

region = "us-west-2"

# Configure the AWS provider
aws_provider = aws.Provider("aws", region=region)

# Create security group
minecraft_sg = aws.ec2.SecurityGroup(
    "minecraft_sg",
    description="Allow Minecraft traffic",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=25565,
            to_port=25565,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create VPC
minecraft_vpc = aws.ec2.Vpc(
    "minecraft_vpc",
    cidr_block="10.0.0.0/16",
    tags={"Name": "minecraft_vpc"},
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create subnet
minecraft_subnet = aws.ec2.Subnet(
    "minecraft_subnet",
    vpc_id=minecraft_vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "minecraft_subnet"},
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create internet gateway
minecraft_gw = aws.ec2.InternetGateway(
    "minecraft_gw",
    vpc_id=minecraft_vpc.id,
    tags={"Name": "minecraft_gw"},
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create route table
minecraft_route_table = aws.ec2.RouteTable(
    "minecraft_route_table",
    vpc_id=minecraft_vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=minecraft_gw.id,
        )
    ],
    tags={"Name": "minecraft_route_table"},
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Associate route table with subnet
aws.ec2.RouteTableAssociation(
    "minecraft_route_table_association",
    subnet_id=minecraft_subnet.id,
    route_table_id=minecraft_route_table.id,
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Get ECS optimized AMI ID
ecs_ami_id = aws.ssm.get_parameter(
    name="/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
)

# Create ECS cluster
minecraft_cluster = aws.ecs.Cluster(
    "minecraft_cluster", opts=pulumi.ResourceOptions(provider=aws_provider)
)

# Create log group
minecraft_log_group = aws.cloudwatch.LogGroup(
    "minecraft_log_group",
    retention_in_days=7,
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create IAM role for ECS task execution
ecs_execution_role = aws.iam.Role(
    "ecs_execution_role",
    assume_role_policy=pulumi.Output.all(service="ecs-tasks.amazonaws.com").apply(
        lambda args: {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {"Service": args["service"]},
                }
            ],
        }
    ),
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Attach policy to IAM role
aws.iam.RolePolicyAttachment(
    "ecs_execution_role_policy_attachment",
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    role=ecs_execution_role.name,
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create ECS task definition
minecraft_task = aws.ecs.TaskDefinition(
    "minecraft_task_definition",
    family="minecraft_task",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    cpu="1024",
    memory="2048",
    execution_role_arn=ecs_execution_role.arn,
    container_definitions=pulumi.Output.all(
        log_group_name=minecraft_log_group.name,
    ).apply(
        lambda args: json.dumps(
            [
                {
                    "name": "minecraft_container",
                    "image": "itzg/minecraft-server",
                    "cpu": 512,
                    "memory": 1024,
                    "essential": True,
                    "portMappings": [
                        {"containerPort": 25565, "hostPort": 25565, "protocol": "tcp"}
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": args["log_group_name"],
                            "awslogs-region": region,
                            "awslogs-stream-prefix": "minecraft-server",
                        },
                    },
                }
            ]
        )
    ),
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create ALB target group
minecraft_target_group = aws.lb.TargetGroup(
    "minecraft_target_group",
    port=25565,
    protocol="TCP",
    vpc_id=minecraft_vpc.id,
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create ECS service
minecraft_service = aws.ecs.Service(
    "minecraft_service",
    cluster=minecraft_cluster.id,
    task_definition=minecraft_task.arn,
    desired_count=1,
    launch_type="FARGATE",
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        assign_public_ip=True,
        subnets=[minecraft_subnet.id],
        security_groups=[minecraft_sg.id],
    ),
    load_balancers=[
        aws.ecs.ServiceLoadBalancerArgs(
            target_group_arn=minecraft_target_group.arn,
            container_name="minecraft_container",
            container_port=25565,
        )
    ],
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create Application Load Balancer (ALB)
minecraft_alb = aws.lb.LoadBalancer(
    "minecraft_alb",
    internal=False,
    security_groups=[minecraft_sg.id],
    subnets=[minecraft_subnet.id],
    opts=pulumi.ResourceOptions(provider=aws_provider),
)

# Create ALB listener
minecraft_listener = aws.lb.Listener(
    "minecraft_listener",
    load_balancer_arn=minecraft_alb.arn,
    port=25565,
    protocol="TCP",
    default_actions=[
        aws.lb.ListenerDefaultActionArgs(
            type="forward",
            target_group_arn=minecraft_target_group.arn,
        )
    ],
    opts=pulumi.ResourceOptions(provider=aws_provider),
)
