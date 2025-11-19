variable "cluster_name" {
    description = "Name of the EKS cluster and related resources"
    type = string
}

variable "vpc_id" {
    description = "VPC ID"
    type = string
}

variable "public_subnet_ids" {
    description = "Public Subnet ID(s)"
    type = list(string)
}

variable "private_subnet_ids" {
    description = "Private Subnet ID(s)"
    type = list(string)
}

