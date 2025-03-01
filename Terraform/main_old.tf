################################################################################
# Providers
################################################################################


provider "aws" {
  region = var.region
  default_tags {
    tags = local.aws_default_tags
  }
}


provider "kubernetes" {
  host                   = data.aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", var.eks_cluster_name]
  }
}


provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.main.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
    exec {
      api_version = "client.authentication.k8s.io/v1alpha1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", var.eks_cluster_name]
    }
  }
}


data "aws_eks_cluster" "main" {
  name = var.eks_cluster_name
}


################################################################################
# Local Variables
################################################################################


locals {
  aws_default_tags = merge(
    { "clusterName" : var.eks_cluster_name },
    var.aws_default_tags,
  )
  customer_identifier         = trimprefix(var.eks_cluster_name, "wv-")
  customer_cluster_identifier = "prod-dedicated-enterprise"
}


################################################################################
# EKS Cluster and VPC Configuration
################################################################################


# (Intentionally left blank for exercise)


################################################################################
# High Availability Setup for Weaviate
################################################################################


module "weaviate_helm" {
  source = "./modules/weaviate"
  # ... (existing configuration)


  # HA Setup
  replica_count = 2


  # Weaviate-specific configurations
  weaviate_replication_factor = 1


  # Node Affinity and Anti-Affinity (to spread pods across AZs)
  affinity = {
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


  # Tolerations (if needed based on your taints setup)
  tolerations = [
    # Tolerations configuration here
  ]


  # Persistent Volume Claim Issue
  volume_claim_templates = [{
    metadata = {
      name = "weaviate-data"
    }
    spec = {
      accessModes = ["ReadWriteOnce"]
      resources = {
        requests = {
          storage = "10Gi"
        }
      }
    }
  }]


  depends_on = [
    kubernetes_namespace.weaviate-namespace
  ]
}


################################################################################
# Additional Modules and Resources
################################################################################


# What additional modules should be added here?


################################################################################
# Kubernetes Namespace for Weaviate
################################################################################


resource "kubernetes_namespace" "weaviate-namespace" {
  metadata {
    name = var.namespace
  }
}



