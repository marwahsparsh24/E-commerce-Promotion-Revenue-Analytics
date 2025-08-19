# E-commerce Promotion Revenue Analytics

A production-style data pipeline that transforms ecommerce promotion & revenue raw data into analytics-ready **facts & dimensions** on **Snowflake**, orchestrated by **Apache Airflow** via **Astronomer Cosmos**.

---

## Stack

- **Transform:** dbt Core + dbt-Snowflake  
- **Warehouse:** Snowflake  
- **Orchestration:** Airflow + Astronomer Cosmos  
- **Testing:** dbt generic & singular tests

---

## Repository Layout (choose ONE dbt project as source of truth)

```
data_engg_proj/
├─ dbt-dag/                  # Airflow project (DAGs, Cosmos)
│  └─ dags/
│     └─ dbt/ data_pipeline/ # (Option A) dbt project here
└─ data_pipeline/            # (Option B) standalone dbt project
```

> **Best practice:** keep the dbt project **outside** `dags/` (Option B), and point Cosmos to that folder.

---

## Prerequisites

- Snowflake account & role with create/usage privileges  
- Python 3.12+ and Git  
- Docker (for running Airflow locally)  
- Keep **secrets out of git** (`~/.dbt/profiles.yml`, passwords, tokens)

---

## 1) dbt Setup (install → init → verify)

Install dbt and the Snowflake adapter, then initialize your project:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install "dbt-core==1.10.0" "dbt-snowflake==1.10.0"
dbt --version

# choose ONE location; example uses a top-level project
dbt init data_pipeline
```

During `dbt init`, provide Snowflake details:

- Account: `fbc00712.us-east-1` (no `https://`, no domain)  
- User / Password: your Snowflake credentials *(or use SSO later)*  
- Role: `DBT_ROLE` • Warehouse: `DBT_WH` • Database: `DBT_DB` • Schema: `DBT_SCHEMA` • Threads: 4–8  
- Keep session alive: **Yes**

Then:

```bash
cd data_pipeline
dbt deps
dbt debug
```

---

## 2) Snowflake Bootstrap (one-time)

Run once as an admin (e.g., `SYSADMIN`):

```sql
use role accountadmin;

create warehouse dbt_wh with warehouse_size = 'x-small';
create database dbt_db;
create role dbt_role;

show grants on warehouse dbt_wh;

grant usage on warehouse dbt_wh to role dbt_role;
grant role dbt_role to user <USERNAME>;
grant all on database dbt_db to role dbt_role;

use role dbt_role;

create schema dbt_db.dbt_schema;
```

---

## 3) Materialize the Schema (staging → intermediate → marts)

- **Staging (`stg_*`)** — clean & standardize sources (often **views**)  
- **Intermediate (`int_*`)** — reusable joins & calculations (often **tables**)  
- **Marts (`dim_*`, `fct_*`)** — business-facing dims/facts (**tables**) with surrogate keys & tests

Set defaults in your `dbt_project.yml` (project root):

```yaml
models:
  <project_name>:
    staging:      +materialized: view
    intermediate: +materialized: table
    marts:        +materialized: table
```

Add `dbt_utils` to `packages.yml`:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: "1.3.0"
```

---

## 4) Build Required Tables (run & test)

```bash
dbt deps
dbt run         # or run subsets: dbt run -s staging intermediate marts
dbt test
```

Outputs: `dim_*` and `fct_*` relations in `DBT_DB.DBT_SCHEMA`.

---

## 5) Orchestrate with Airflow (Cosmos) — optional

1. Ensure Airflow environment has:
   ```bash
   pip install "apache-airflow-providers-snowflake" "astronomer-cosmos>=1.9,<2" "dbt-snowflake==1.10.0"
   ```
2. In Airflow **Admin → Connections**, create **`Snowflake_conn`**  
   - Host: `<ACC_NAME>`  
   - Extra JSON:
     ```json
     {
       "account": "<ACC_NAME>",
       "warehouse": "DBT_WH",
       "database": "DBT_DB",
       "role": "DBT_ROLE",
       "authenticator": "snowflake"
     }
     ```
     *(Use `"externalbrowser"` for SSO and leave Password empty.)*
3. In your DAG code, point Cosmos’ `ProjectConfig` to the **folder that contains `dbt_project.yml`**.  
4. Start Airflow, unpause **dbt_dag**, and **Trigger** it.

---

## Data Quality

- **Generic tests:** `unique`, `not_null`, `relationships`, `accepted_values`  
- **Singular tests:** custom SQL for business rules  
- Run with `dbt test`

---

## Troubleshooting

- **Account format:** `<ACC_NAME>` (no protocol/domain)  
- **Auth:** use `authenticator: snowflake` for user/password; `externalbrowser` for SSO  
- **Permissions:** ensure role grants on warehouse/database/schema (see bootstrap SQL)  
- **Cosmos path:** point to the **folder** (not the file) that has `dbt_project.yml`  
- **Airflow error “multiple values for dag_id”:** pass only keyword args to `DbtDag` (or make the first positional arg the `dag_id`)

---

## .gitignore (recommended)

```
.DS_Store
__pycache__/
*.pyc
.venv/
venv/
logs/
.astro/
.env
*.log
data_pipeline/target/
data_pipeline/logs/
data_pipeline/dbt_packages/
dbt-dag/dags/**/target/
dbt-dag/dags/**/logs/
dbt-dag/dags/**/dbt_packages/
.vscode/
.idea/
```

---
