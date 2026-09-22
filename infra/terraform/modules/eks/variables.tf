variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "url_shortener_cluster"
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS cluster"
  type        = string
  default     = "1.35"
}

variable "node_group_name" {
  description = "name of the node group"
  type        = string
  default     = "eks_url_shortner_ng"
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the EKS cluster and worker nodes"
  type        = list(string)
}

variable "node_instance_types" {
  description = "EC2 instance types for the worker node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}
