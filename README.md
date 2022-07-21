# Self-healing Apache Zookeeper ECS cluster

## General information
The repository is a fork of https://github.com/dethmix/self-healing-zookeeper. self-healing-zookeeper deploys each instance of the zookeeper cluster as a separate service. It then uses ECS cloud map to discover its peers in the cluster.

With this repo we aim to deploy zookeeper with lesser number of components. Instead of keeping each of the zookeeper cluster instances as part of separate services, we combine them into 1 single service. We used the underlying behavior of how containers are scheduled in a service when there are multiple subnets. If the service has multiple subnets, each replica that comes up for the service will attach to the subnet that has no containers in that subnet. This constitutes the basic principle of our deployment strategy.

## Usage
Terraform code can be found in `terraform` directory, just update variable.tf file with values related to your AWS VPC and execute `terraform plan && terraform apply`


## Infrastructure

The infrastructure required to implement this solution are the following:

Number of subnets equal to the number of ZK instances desired to be in the zookeeper cluster. Note: Each subnet houses a single instance of a cluster.

When the container comes up in the respective subnets, there are 2 requirements for that container to be part of the zookeeper cluster.
- The container needs to update its IP with correct domain in route53. We have provided that intelligence to the container where they register the domain appropriately with route53.
- The container needs to assign the correct zookeeper id to itself to be part of the zookeeper cluster

We automated the Zookeeper node deployment by adding DNS names in the configs instead of IP addresses while defining the members of the zookeeper cluster. This ensures that we don't have to change the IP address again when have to deploy zookeeper.

We need to create a hosted zone on AWS rotute53 so that DNS can be updated.

e.g
```
ZOO_HOSTED_ZONE=T24WYUCZ179
```

Every zookeeper instance that comes up as a cluster needs to have a predetermined ID. We use the third octet of the subnet CIDR to assign the ID value for the zookeeper instance.


If the subnet is `10.1.101.0/24` then the Zookeeper server value should be `101=101.domain.local:2888:3888;2181` by getting the third octet value from the subnet cidr.

e.g
```
ZOO_SERVERS=101=101.domain.local:2888:3888;2181 102=102.domain.local:2888:3888;2181 103=103.domain.local:2888:3888;2181
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
Note: Please enable healthchecks as part of task definition so that the health check will ensure that zookeeper initial deployment is handled gracefully.
```
      "healthCheck": {
        "retries": 5,
        "command": [
          "CMD-SHELL",
          "python3 check_status.py | grep -iw 'all OK' || exit 1"
        ],
        "timeout": 30,
        "interval": 60,
        "startPeriod": 120
      },
```
