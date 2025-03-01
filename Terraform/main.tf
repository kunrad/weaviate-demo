################################################################################################
# Terraform 
# This file is used to configure the Terraform provider and modules
################################################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" #versions are suggested
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

################################################################################################
# Provider Configuration
################################################################################################

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
    api_version = local.api_version
    command     = local.command
    args        = local.args
  }
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.main.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data)
    exec {
      api_version = local.api_version
      command     = local.command
      args        = local.args
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
  customer_cluster_identifier = var.customer_cluster_identifier #parameterized to make it reuseable
  api_version                 = var.api_version                 #inconsistency with the API version && parameterized to make it reuseable
  command                     = var.command                     #parameterized to make it reuseable
  args                        = var.args                        #parameterized to make it reuseable
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
  replica_count = var.replica_count # parameterized to make it reuseable


  # Weaviate-specific configurations
  weaviate_replication_factor = var.weaviate_replication_factor #maintain consistency with the replica count for true HA configurations && parameterized 

  # Node Affinity and Anti-Affinity (to spread pods across AZs)
  set {
    name  = "affinity"
    value = jsonencode(var.affinity) # parameterized the value for the affinity
  }

  # Tolerations (if needed based on your taints setup)
  tolerations = var.weaviate_tolerations # parameterized the tolerations to make it reuseable


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
      storageClassName = var.weaviate_volume_claim_storage_class_name # parameterized the storage class
    }
  }]

  depends_on = [
    kubernetes_namespace.weaviate-namespace
  ]
}

resource "kubernetes_namespace" "weaviate-namespace" {
  metadata {
    name = var.namespace
  }
}
