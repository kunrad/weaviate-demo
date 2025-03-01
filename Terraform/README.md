## Provider Configuration Block

### a. Inconsistent API Versions in exec block

* Issue: The Kubernetes provider was `api_version = "client.authentication.k8s.io/v1beta1"`. while the helm chart uses `v1alpha1` in its exec block.
* Enhancement: Use a consistent API version for token retrieval across providers to avoid potential compatibility issues. Also ensure the version is supported by the current K8s version.

### b. Duplication of Cluster Connection Details

* Issue: Both the k8s and Helm provider configure the connection using the EKS cluster endpoint, certificate and exec block.
* Enhancement: Extracted the shared values to keep it DRY

### c. Provider Version Pinning

* Issue: There was no version pinning for the providers
* Enchancement: Based on the configurations, I have created `required_version` for all providers. I used an extimated value for the version numbers.

## Local Variables Block

### a. Harcoded Customer Cluster Identifier

* Issue: The local variable `customer_cluster_identifier` is set to `"prod-dedicated-enterprise"`, which might be too rigid
* Enhancement: Parameterized it by making it a variable so it can be reusable

## Helm Module Block 🚀️

### a. Mismatch in Replication Settings

* **Issue:** The module sets `replica_count = 2` (implying HA) while the `weaviate_replication_factor` is set to 1.
* **Enhancement:** The replication factor should align with the number of replicas for true high availability. The replication factor should match the replica count except there’s a specific reason for this difference.

### b. Incomplete Tolerations Block

* **Issue:** The `tolerations` block is present but does not have the required configuration
* **Enhancement:** Based on the taint configurations I have also added parameterized values for the toleration block this also makes it reuseable

### c. Parameterized the values for affinity

* My assumption here is that there could be various taint configurations for the different Clusters. This should make the configuration reusable for multiple K8s Clusters.

### c. Volume Claim Templates

* **Issue:** The persistent volume claim (PVC) is defined with a fixed storage size and access mode without reference to storage classes or dynamic provisioning.
* **Enhancement:** Parameterized and explicitly setting a storage class. This improves flexibility and compatibility with different Kubernetes environments.
