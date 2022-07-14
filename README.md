# Self-healing Apache Zookeeper ECS cluster

## General information
The repository is a fork from https://github.com/dethmix/self-healing-zookeeper which the goal is to have a Zookeeper server that is self-healing and is deployed in AWS ECS, this has been further improved by removing the ECS autodiscovery feature as it creates complexity during deployment and automate the Zookeeper node enrollment.

## Usage
Terraform code can be found in `terraform` directory, just update variable.tf file with values related to your AWS VPC and execute `terraform plan && terraform apply`


## Infrastructure

The infrastructure required to implement this solution is an EC2 container instance with a minimum of 3 subnets in which each subnet is equivalent to one container. 

We also automated the Zookeeper node deployment by just adding a DNS instead of an IP addresses as the endpoint, this make sure that we are not changing the IP address again whenever we want to reroll the containers.

One requirement for this is to create a AWS Private Hosted Zone entry and put the hosted zone id to the environments in the task definition.

e.g
```
ZOO_HOSTED_ZONE=T24WYUCZ179
```

The domain name convention should be configured in a way that it coincides with whatever value the subnet (third octet of the subnet cidr) has. 


If the subnet is 10.1.101.0/24 then the Zookeeper server value should be 101.101.domain.local:2888:3888;2181 by getting the third octet value from the subnet cidr.

e.g
```
ZOO_SERVERS=101=101.domain.local:2888:3888;2181 102=domain.local:2888:3888;2181 103=103.domain.local:2888:3888;2181
```

As for the permission, the task role should have a policy to create and update the specific AWS Private Hosted Zone entry.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "route53:ChangeResourceRecordSets",
            "Resource": "arn:aws:route53:::hostedzone/T24WYUCZ179"
        }
    ]
}
```
