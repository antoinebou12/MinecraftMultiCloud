
provider "aws" {
  region = "us-west-2"
}

resource "aws_security_group" "minecraft_sg" {
  name = "minecraft_sg"

  ingress {
    from_port   = 25565
    to_port     = 25565
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "minecraft_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "minecraft_vpc"
  }
}

resource "aws_subnet" "minecraft_subnet" {
  vpc_id                  = aws_vpc.minecraft_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "minecraft_subnet"
  }
}

resource "aws_internet_gateway" "minecraft_gw" {
  vpc_id = aws_vpc.minecraft_vpc.id

  tags = {
    Name = "minecraft_gw"
  }
}

resource "aws_route_table" "minecraft_route_table" {
  vpc_id = aws_vpc.minecraft_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.minecraft_gw.id
  }

  tags = {
    Name = "minecraft_route_table"
  }
}

resource "aws_route_table_association" "minecraft_route_table_association" {
  subnet_id      = aws_subnet.minecraft_subnet.id
  route_table_id = aws_route_table.minecraft_route_table.id
}

resource "aws_instance" "minecraft_instance" {
  ami           = data.aws_ssm_parameter.ecs_ami_id.value
  instance_type = "t3.medium"

  key_name = "your_key_pair" # Replace with your key pair

  vpc_security_group_ids = [aws_security_group.minecraft_sg.id]

  subnet_id = aws_subnet.minecraft_subnet.id

  tags = {
    Name = "minecraft_instance"
  }
}

data "aws_ssm_parameter" "ecs_ami_id" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}

resource "aws_ecs_cluster" "minecraft_cluster" {
  name = "minecraft_cluster"
}


resource "aws_ecs_task_definition" "minecraft_task" {
  family                   = "minecraft_task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"

  execution_role_arn = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    "name" : "minecraft_container",
    "image" : "itzg/minecraft-server",
    "cpu" : 512,
    "memory" : 1024,
    "essential" : true,
    "portMappings" : [
      {
        "containerPort" : 25565,
        "hostPort" : 25565,
        "protocol" : "tcp"
    }
  ],

  "logConfiguration" : {
    "logDriver" : "awslogs",
    "options" : {
      "awslogs-group" : aws_cloudwatch_log_group.minecraft_log_group.name,
      "awslogs-region" : "us-west-2",
      "awslogs-stream-prefix" : "minecraft-server"
      }
  }
}])
}

resource "aws_cloudwatch_log_group" "minecraft_log_group" {
  name = "minecraft_log_group"
  retention_in_days = 7
}

resource "aws_ecs_service" "minecraft_service" {
  name = "minecraft_service"
  cluster = aws_ecs_cluster.minecraft_cluster.id
  task_definition = aws_ecs_task_definition.minecraft_task.arn
  desired_count = 1

  launch_type = "FARGATE"

  network_configuration {
    assign_public_ip = true
    subnets = [aws_subnet.minecraft_subnet.id]
    security_groups = [aws_security_group.minecraft_sg.id]
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.minecraft_target_group.arn
    container_name = "minecraft_container"
    container_port = 25565
  }

  depends_on = [aws_alb_listener.minecraft_listener]
}

resource "aws_alb" "minecraft_alb" {
  name = "minecraft-alb"
  internal = false
  security_groups = [aws_security_group.minecraft_sg.id]
  subnets = [aws_subnet.minecraft_subnet.id]
}

resource "aws_alb_target_group" "minecraft_target_group" {
  name = "minecraft-target-group"
  port = 25565
  protocol = "TCP"
  vpc_id = aws_vpc.minecraft_vpc.id
}

resource "aws_alb_listener" "minecraft_listener" {
  load_balancer_arn = aws_alb.minecraft_alb.arn
  port = 25565
  protocol = "TCP"

  default_action {
    type = "forward"
    target_group_arn = aws_alb_target_group.minecraft_target_group.arn
  }
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
    {
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      }
      ]
      })
  }

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role = aws_iam_role.ecs_execution_role.name
}