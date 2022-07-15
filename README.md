# Self-healing Apache Zookeeper ECS cluster

## General information
The repository is a fork from https://github.com/dethmix/self-healing-zookeeper. self-healing-zookeeper deploys each instance of the zookeeper cluster as a separate service. It then uses ECS cloud map to discover its peers in the cluster.

With this repo we aimed to provide this with lesser number of moving parts. Instead of keeping the cluster nodes as part of separate services, we combined them into 1 single service. We used the underlying behavior of how nodes are scheduled in a service when there are multiple subnets. If the service has multiple subnets, each replica that comes up for the service will attach to the subnet that has no instances in that subnet.
## Usage
Terraform code can be found in `terraform` directory, just update variable.tf file with values related to your AWS VPC and execute `terraform plan && terraform apply`


## Infrastructure

The infrastructure required to implement this solution are the following:

Number of subnets equal to the number of nodes desired to be in the cluster
Note: Each subnet houses a single instance of a cluster.

When the container comes up in the respective subnets, there are 2 requirements for that container to be part of the zookeeper cluster.
- The container needs to update its IP with correct domain in route53. We have provided that intelligence to the container where they register the domain appropriately with route53.
- The container needs to assign the correct zookeeper id to itself to be part of the zookeeper cluster

We automated the Zookeeper node deployment by adding DNS names in the configs instead of IP addresses while defining the members of the zookeeper cluster. This ensures that we don't have to change the IP address again when we want to deploy zookeeper.

e.g
```
ZOO_HOSTED_ZONE=T24WYUCZ179
```

The domain name convention should be configured in a way that it coincides with whatever value the subnet (third octet of the subnet cidr) has. 


If the subnet is 10.1.101.0/24 then the Zookeeper server value should be 101.101.domain.local:2888:3888;2181 by getting the third octet value from the subnet cidr.

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
