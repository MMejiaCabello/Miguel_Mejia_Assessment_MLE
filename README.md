# 🏆 Assessment Técnico – Machine Learning Engineer (MLE)

Este repositorio contiene la **solución completa** al *Assessment Técnico – MLE* compuesto por 5 retos principales.  
El objetivo es demostrar habilidades en **MLOps, pipelines en GCP, IaC, versionado, monitoreo y análisis de tecnologías emergentes**.

---

## 📂 Estructura del Repositorio

```sh
Miguel_Mejia_Assessment_MLE/
│
├── 01_pipeline_ml/             # Pipeline E2E en GCP (Vertex AI Pipelines)
│ ├── src/                      # Código fuente de componentes
│ ├── notebooks/                # Notebooks de ingesta y exploración
│ ├── compiled/                 # Pipelines compilados (.yaml)
│ ├── diagram.png               # Diagrama visual del pipeline
│ ├── churn_pipeline.py         # Definición del pipeline KFP
│ ├── run_pipeline.py           # Ejecución en Vertex AI
│ ├── compile_pipeline.py       # Compilación a YAML
│ └── README.md
│
├── 02_terraform_infra/         # Infraestructura como Código (IaC)
│ ├── main.tf
│ ├── variables.tf
│ ├── outputs.tf
│ ├── modules/
│ └── README.md
│
├── 03_versioning_retraining/   # Versionado y Reentrenamiento
│ ├── mlflow_setup/
│ ├── compare_metrics.py
│ └── README.md
│
├── 04_monitoring_eval/         # Evaluación y Monitoreo del Modelo
│ ├── monitoring_simulation.ipynb
│ └── README.md
│
└── 05_bonus_investigacion/     # Investigación Tecnológica
└── llmops_gcp_ml_factory.md

```

---

## 📜 Descripción de los Retos

### **1. Pipeline E2E en GCP** (30 pts)
- **Objetivo:** Diseñar un pipeline completo para predecir **churn** de clientes (`clientes.csv`).
- **Etapas cubiertas:**
  1. Ingesta y conversión a Parquet ([`load_data.py`](../01_pipeline_ml/src/ingestion/load_data.py))
  2. Feature Engineering
  3. Preprocesamiento
  4. Entrenamiento con **XGBoost**
  5. Registro en **Model Registry** si el AUC ≥ `threshold`
- **Ejecución:**
  ```bash
  python compile_pipeline.py
  python run_pipeline.py
  ```

### **2. Infraestructura como Código – Terraform** (20 pts)
- **Objetivo:** Desplegar en GCP los recursos mínimos para soportar el pipeline:
   - Bucket en GCS
   - Dataset en BigQuery
   - Configuración Vertex AI
   - Roles IAM mínimos
 
- **Ejecución:**
  ```bash
  terraform init
  terraform plan
  terraform apply
  ```
  
### **3. Versionado y Reentrenamiento** (20 pts)
- **Objetivo:**  Implementar versionado con `MLflow` o `DVC` y reentrenar automáticamente si la métrica supera el umbral.

 
- **Flujo:**
  1. Comparar métricas (`compare_metrics.py`)
  2. Si se supera el AUC, dispara reentrenamiento
  
  
### **4. Evaluación y Monitoreo** (20 pts)
- **Objetivo:** Describir/simular un sistema de monitoreo:
   - Métricas de rendimiento
   - Alertas automáticas
   - Test A/B
   - Estrategia de rollback
   
- **Archivo clave:** `monitoring_simulation.ipynb`

### **5. Bonus – Investigación Tecnológica** (10 pts)
- **Objetivo:** Describir una tecnología emergente (`LLMOps`) y su integración en una ML Factory sobre GCP.

--- 
 
 ### **🚀 Requisitos**
   - Python 3.10+
   - Poetry
   - Google Cloud SDK
   - Terraform