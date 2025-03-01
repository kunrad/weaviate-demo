variable "region" {
  description = "The AWS region to deploy resources"
  type        = string
}

variable "eks_cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
}

variable "aws_default_tags" {
  description = "A map of default tags to apply to all resources"
  type        = map(string)
}

variable "customer_cluster_identifier" {
  description = "The identifier for the customer cluster"
  type        = string
  default     = "prod-dedicated-enterprise"
}

variable "api_version" {
  description = "The API version to use for the Kubernetes provider"
  type        = string
  default     = "client.authentication.k8s.io/v1beta1"
}

variable "command" {
  description = "The command to use for the Kubernetes provider"
  type        = string
  default     = "aws"
}

variable "args" {
  description = "The arguments to use for the Kubernetes provider"
  type        = list(string)
  default     = ["eks", "get-token", "--cluster-name", var.eks_cluster_name]
}

variable "replica_count" {
  description = "The number of replicas to use for the Kubernetes provider"
  type        = number
  default     = 2
}

variable "weaviate_replication_factor" {
  description = "value of the replication factor"
  type        = number
  default     = 2
}

variable "affinity" {
  description = "affinity configuration for pods in Helm chart"
  type        = any
  default = {
    podAntiAffinity = {
      requiredDuringSchedulingIgnoredDuringExecution = [
        {
          labelSelector = {
            matchExpressions = [
              {
                key      = "app"
                operator = "In"
                values   = ["weaviate"]
              },
            ]
          },
          topologyKey = "topology.kubernetes.io/zone"
        },
      ]
    }
  }

}
variable "weaviate_tolerations" {
  description = "The tolerations to apply to the Weaviate pods"
  type = list(object({
    key      = string
    operator = string
    value    = string
    effect   = string
  }))
  default = [
    {
      key      = "app"
      operator = "Equal"
      value    = "weaviate"
      effect   = "NoSchedule"
    }
  ]

}

variable "weaviate_volume_claim_storage_class_name" {
  description = "The storage class name for the Weaviate volume claim"
  type        = string
  default     = "gp2"
}

variable "namespace" {
  description = "The namespace to deploy Weaviate into"
  type        = string
  default     = "weaviate"

}