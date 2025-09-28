# Delivery App Deployment & Migration Plan

## 🚀 Migration Path

### Phase 1: MVP on DigitalOcean (~$50/month)
**Goal:** Develop quickly, keep costs low.

- **Compute:**
  - 1 Droplet (2 vCPU, 4GB) running Django + React build + Celery.
- **Database:**
  - Managed PostgreSQL (1 vCPU, 1GB).
- **Storage:**
  - DigitalOcean Spaces (S3-compatible) for media.
- **Networking:**
  - Direct droplet access (no load balancer yet).
- **CI/CD:**
  - GitHub Actions → deploy via `doctl`.

👉 Single node, simple config, minimal monthly cost.

---

### Phase 2: Pre-Production (Scaling on DigitalOcean, ~$120–150/month)
**Goal:** Handle more users, prepare for migration.

- **Compute:**
  - Split into:
    - 2 App Droplets (load-balanced).
    - 1 Worker Droplet (Celery).
- **Database:**
  - Upgrade PostgreSQL to 2 vCPU, 4GB.
- **Networking:**
  - DigitalOcean Load Balancer ($12/mo).
- **Monitoring:**
  - Enable DO Monitoring + Logging.
- **Deployment:**
  - Dockerize app to make migration easier.

👉 At this point, app architecture is **cloud-portable**.

---

### Phase 3: Production on AWS (~$200–240/month)
**Migration path from DigitalOcean:**

- **Compute:**
  - Move Django app to **Elastic Beanstalk** or **ECS/Fargate**.
  - Celery workers → separate ECS service or EC2 instance.
- **Database:**
  - Migrate DO Postgres → **AWS RDS Postgres**.
  - Use pg_dump/pg_restore for data transfer.
- **Storage:**
  - Move Spaces → **AWS S3**.
- **Networking:**
  - Add **AWS ALB (Application Load Balancer)**.
- **Monitoring:**
  - **CloudWatch** for logs/metrics.
- **CI/CD:**
  - GitHub Actions → AWS CodeDeploy or direct ECS deploys.

---

### Phase 3: Production on Azure (~$210–250/month)
**Migration path from DigitalOcean:**

- **Compute:**
  - Move Django app to **Azure App Service (Linux)**.
  - Celery workers → **Azure Container Apps** or VM Scale Set.
- **Database:**
  - Migrate DO Postgres → **Azure Database for PostgreSQL (Flexible Server)**.
- **Storage:**
  - Spaces → **Azure Blob Storage**.
- **Networking:**
  - Use **Azure Front Door** or Load Balancer.
- **Monitoring:**
  - **Azure Monitor + Application Insights**.
- **CI/CD:**
  - GitHub Actions → Azure Web App Deploy.

---

## 🔄 Migration Steps (DO → AWS/Azure)
1. **Containerize everything** (Docker) → ensures portability.  
2. **Abstract storage** (use S3 API-compatible SDKs) → so Spaces → S3/Blob is just config change.  
3. **Use environment variables & secrets managers** → avoid hardcoding infra details.  
4. **For DB migration**:

   ```bash
   # Dump from DigitalOcean
   pg_dump -Fc --no-acl --no-owner -h <DO_HOST> -U <USER> <DBNAME> > backup.dump

   # Restore into AWS/Azure
   pg_restore --no-acl --no-owner -h <NEW_HOST> -U <USER> -d <DBNAME> backup.dump
   ```

5. **Switch DNS gradually** → point traffic from DO → AWS/Azure once tested.

---

✅ With this approach:
- **MVP** → fast & cheap on DigitalOcean.
- **Production** → lift-and-shift to AWS or Azure with minimal rewrite (mostly infra changes).
