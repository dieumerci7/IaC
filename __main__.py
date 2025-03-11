import pulumi
import pulumi_aws as aws
from variables import AWS_REGION, AMI_ID, INSTANCE_TYPE, INSTANCE_NAMES, SSH_KEYS

aws_provider = aws.Provider("aws-provider", region=AWS_REGION)

key_pair = aws.ec2.KeyPair("deployer-key", public_key=SSH_KEYS[0])

# For the second key
user_data = f"""#!/bin/bash
echo "{SSH_KEYS[1]}" >> /home/ubuntu/.ssh/authorized_keys
"""

security_group_ssh = aws.ec2.SecurityGroup(
    "ssh-sg",
    description="Allow SSH access",
    ingress=[
        # Allow SSH (port 22) for everyone
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[
        # No outbound restrictions
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
    ]
)

instances = []
for name in INSTANCE_NAMES:
    instance = aws.ec2.Instance(
        name,
        ami=AMI_ID,
        instance_type=INSTANCE_TYPE,
        key_name=key_pair.key_name,
        vpc_security_group_ids=[security_group_ssh.id],
        user_data=user_data,
        tags={"Name": name},
        opts=pulumi.ResourceOptions(provider=aws_provider),
    )
    instances.append(instance)

postgresql_sg = aws.ec2.SecurityGroup(
    "postgresql-sg",
    description="Allow PostgreSQL access between instances",
    ingress=[
        # Only allow PostgreSQL from our servers' IPs
        {
            "protocol": "tcp",
            "from_port": 5432,
            "to_port": 5435,
            "cidr_blocks": [
                pulumi.Output.concat(instances[0].private_ip, "/32"),
                pulumi.Output.concat(instances[1].private_ip, "/32")
            ]
        },
    ],
    egress=[
        # No outbound restrictions
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
    ]
)

for i, instance in enumerate(instances):
    aws.ec2.NetworkInterfaceSecurityGroupAttachment(
        f"sg-attachment-{i}",
        security_group_id=postgresql_sg.id,
        network_interface_id=instance.primary_network_interface_id
    )

pulumi.export("server-1-public-ip", instances[0].public_ip)
pulumi.export("server-2-public-ip", instances[1].public_ip)
pulumi.export("server-1-private-ip", instances[0].private_ip)
pulumi.export("server-2-private-ip", instances[1].private_ip)