# Post-Mortem Analysis: Databricks Connectivity Loss 🚨

**Incident Summary:**

This was implemented fully by the Network Engineering Team, DevOps team and DataScience team.

**Network Engineering Team**: Managed the network connection between databricks and our internal network.

**DevOps Team**: Implemented the CICD pipeline to create a private link to databricks and allow the IPs give by the Network team access to the application.

**DataScience Team**: Tested all jobs in a controlled environment and ensured they were all executing.


On **[timstamp]**, during the rollout of our new private connectivity setup between our cloud environment and managed Databricks, we experienced an unexpected connectivity loss. This incident disrupted data processing pipelines and impacted analytics workflows for approximately 2 hours. Our investigation revealed that misconfigurations in our private endpoint settings, associated network routing were the root cause and a lack of proper controlled test to simulate expections of most jobs.

---

## Timeline of Events

* **[timestamp]:** While migrating from our existing databricks environment in Azure to the managed databricks environment, a new private connection configuration was deployed to production following successful tests in the Pre-Prod environment.
* **[timestamp]:** Monitoring systems began reporting intermittent connectivity issues with the managed Databricks workspace.
* **[timestamp]:** There were some widespread failures in data ingestion jobs and interactive notebook sessions which was highlighted by the data team, some jobs were failing.
* **[timestamp]:** An emergency troubleshooting session commenced, during which the team identified that traffic from our cloud environment was not reaching the managed Databricks instance, this was not identified cause of the firewall we had setup and some manual IPs which were not initially setup on our existing CICD pipelines. They were setup in the legacy environment.
* **[timestamp]:** A temporary rollback was initiated, reverting to the previous connectivity setup to restore service.
* **[timestamp]:** Services were fully restored, and a detailed post-incident review was scheduled.
* **[timestamp]**: The IPs were then identified and updated on the CICD pipelines. This then led to the engineering team testing the new setup in a controled workspace to ensure these failures were prevented.

---

## Impact

* **Data Processing Delays:** Batch jobs and ETL processes were halted, leading to delays in data availability for downstream analytics(Tableau).
* **User Disruption:** Data scientists and business analysts experienced reduced productivity due to inaccessibility of interactive Databricks notebooks.
* **Operational Overhead:** The incident required an unscheduled emergency response, impacting overall team productivity and resource allocation.

---

## Root Cause Analysis

* **Misconfigured Private Endpoints:**
  * The new private connectivity configuration assumed default security group and routing settings. However, specific IP whitelisting and DNS resolution rules were not updated in sync with the new endpoints, these were coming from our legacy systems and not updated to our CICD pipelines.
  * The were no explicit modified route table modifications which led to incorrect traffic routing, causing requests to Databricks to be dropped or misdirected.
* **Insufficient Staging Coverage:**
  * Although the configuration passed automated tests in Pre-Prod and Staging, the Pre-Prod environment did not fully replicate the complex network policies present in production, this was because the Pre-Prod environment was relatively new and no having all the routing configurations which were manually created in the legacy production environment as well as all the routing IPs.
  * The Pre-Prod tests lacked realistic simulation of production-scale network traffic and security group interactions.
* **Change Management Oversight:**
  * The deployment plan did not incorporate a phased rollout or comprehensive rollback testing, which would have allowed early detection of the connectivity gap.

---

## Immediate Remediation

1. **Rollback to Previous Configuration:**
   * Reverted the network configuration to the last known good state to quickly restore connectivity and resume critical data workflows.
2. **Hotfix Deployment:**
   * Applied immediate updates to the security group and route table settings, ensuring proper IP whitelisting and DNS configurations for the private endpoints.
   * Tested in batches in a controlled environment to completely simulate expectations of most batch jobs.
3. **Communication:**
   * Issued an incident alert and regular updates to stakeholders, including the analytics and data science teams, explaining the cause and the expected restoration timeline.

---

## Long-Term Corrective Actions

1. **Enhanced Testing Environments:**
   * Develop a more comprehensive staging environment that mirrors production network policies, including realistic simulations of traffic patterns and security configurations.
2. **Improved Change Management:**
   * Implement a phased rollout strategy with canary deployments for critical network changes, ensuring gradual validation and immediate rollback options if anomalies are detected.
3. **Configuration Review Process:**
   * Establish a cross-team review for network and security changes to ensure all related configurations (e.g., security groups, route tables, DNS settings) are updated concurrently inclusive of legacy configurations.
4. **Monitoring and Alerting Upgrades:**
   * Enhance monitoring tools to detect and alert on discrepancies in private endpoint connectivity sooner, enabling faster response times.

---

## Lessons Learned

* **Thorough Testing:**
  * The incident highlighted the need for Pre-prod environments that accurately reflect production complexities, especially for critical infrastructure changes and legacy configurations.
* **Holistic Change Management:**
  * Ensuring that all dependent configurations are considered and validated can prevent unexpected outages during rollouts.
* **Effective Communication:**
  * Transparent, timely communication with all stakeholders minimizes uncertainty and allows teams to adjust work plans during outages.
* **Proactive Monitoring:**
  * Investing in more granular monitoring and alerting can reduce the time to detection and resolution of similar issues in the future.

By learning from this incident and implementing these corrective actions, we worked and improved our infrastructure resilience and prevent future connectivity disruptions when rolling out network-related changes.
