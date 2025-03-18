# AWS region
AWS_REGION = "eu-west-3"

# EC2 params
AMI_ID = "ami-0ff71843f814379b3"
INSTANCE_TYPE = "t3.micro"

# Instance names
INSTANCE_NAMES = ["server-1", "server-2"]

# Public key list
SSH_KEYS = [
    open("ssh-keys/my_key.pub").read().strip(),
    open("ssh-keys/id_ed25519.pub").read().strip(),
]