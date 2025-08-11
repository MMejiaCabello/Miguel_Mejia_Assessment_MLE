# 04_monitoring_eval — Evaluación y Monitoreo del Modelo

Este README documenta por completo el **Punto 4: Evaluación y Monitoreo del Modelo** del *Assessment Técnico – MLE*. Aquí se describe y se **simula** un sistema de monitoreo con métricas, alertas, **test A/B** y **rollback**. Todo está listo para ejecutarse localmente y dejarlo orquestado (Cloud Run Job / Composer / Scheduler) si lo deseas.

> **Repositorio / Carpeta:** `04_monitoring_eval/`

---

## 🎯 Objetivos
1. **Medir desempeño** del modelo de churn (AUC, F1, precisión, etc.).
2. **Detectar drift de datos** mediante **PSI** y gatillar alertas.
3. **Simular A/B testing** para comparar versiones de modelo.
4. **Definir política de rollback** (y ejemplo de split de tráfico en Vertex AI).

---

## 📦 Contenido de la carpeta
```
04_monitoring_eval/
├─ README.md                       ← Este documento
├─ monitoring_notebook.ipynb       ← Demo completa (métricas, PSI, alertas, A/B, rollback)
├─ monitor_metrics.py              ← CLI para monitoreo por lotes (programable)
├─ drift_utils.py                  ← Utilidades de drift (PSI y reporte)
├─ ab_test_sim.py                  ← Utilidad para evaluar A/B y elegir ganador
└─ baseline_metrics.json           ← Baseline de métricas para comparaciones
```

---

## 🧮 Métricas monitoreadas
**Entrenamiento/Validación**
- `accuracy`, `precision`, `recall`, `f1`, `roc_auc` (y `ks` opcional).

**Producción / Post-despliegue (simulado aquí)**
- Degradación de `roc_auc` vs. `baseline`.
- **Drift** de entrada con **PSI** (Population Stability Index).
- (Extensible) Latencia de predicción, tasas de error, throughput, etc.

> En `monitor_metrics.py` las métricas se calculan sobre un batch actual (real o simulado) y se comparan contra un **baseline** previamente generado.

---

## 🔭 Detección de drift con PSI
- **PSI** mide el cambio de distribución entre un conjunto **de referencia** (baseline) y uno **actual**.
- Interpretación típica:
  - PSI < 0.10 → **No significativo**
  - 0.10 ≤ PSI ≤ 0.25 → **Moderado**
  - PSI > 0.25 → **Severo**

**Cálculo (a alto nivel):**
1. Discretizar la variable en *bins* (cuantiles robustos).
2. Calcular proporción por bin en **baseline** y **actual**.
3. Sumar \( (p_{act} - p_{base}) \cdot \ln\frac{p_{act}}{p_{base}} \) en todos los bins.

`drift_utils.py` implementa `population_stability_index()` y `drift_report()` para varias features.

---

## 🚦 Umbrales y reglas de alerta (editables)
En `monitor_metrics.py`:
- `auc_min = 0.75` → si el **ROC AUC** actual es menor, **alerta**.
- `auc_drop_pct_warn = 0.05` → si el AUC cae **≥5%** vs. baseline, **alerta**.
- `psi_warn = 0.10`, `psi_severe = 0.25` → reporta **drift moderado** y **severo** por feature.

Puedes sobreescribirlos con `--thresholds-json path.json`.

---

## ⚙️ Requisitos
- Python 3.9+ (recomendado)
- `pandas`, `numpy`, `scikit-learn`, `matplotlib`
- Dataset `clientes.csv` (local o desde GCS en notebook usando `gcsfs`)

> El notebook ya demuestra cómo cargar `clientes.csv` y correr todo el flujo.

---

## 🛠️ Quickstart (local)
### 1) Crear baseline
Genera (o regenera) el baseline a partir de `clientes.csv`:
```bash
python 04_monitoring_eval/monitor_metrics.py \
  --make-baseline \
  --data-path clientes.csv
```
Esto produce/actualiza `baseline_metrics.json` con: features, métricas y metadatos.

### 2) Ejecutar monitoreo (con drift simulado)
```bash
python 04_monitoring_eval/monitor_metrics.py \
  --data-path clientes.csv \
  --simulate-drift
```
**Salida:**
- Imprime un **reporte JSON** con métricas actuales, caída relativa de AUC y PSI por feature.
- Escribe `monitor_report.json`.
- **Exit code:** `0` si no hay alertas, `1` si hay alertas → útil para orquestadores/alerting.

### 3) Notebook de demo
Abre `monitoring_notebook.ipynb` para ejecutar paso a paso:
- Cálculo de métricas
- PSI + gráfico
- Reglas de alerta
- Simulación **A/B** y selección de ganador
- Política de **rollback**

---

## 📤 Formato de salida (monitor_report.json)
Ejemplo de estructura:
```json
{
  "metrics_current": {"accuracy": 0.82, "precision": 0.64, "recall": 0.59, "f1": 0.61, "roc_auc": 0.78},
  "metrics_baseline": {"accuracy": 0.84, "precision": 0.66, "recall": 0.60, "f1": 0.63, "roc_auc": 0.82},
  "auc_drop_pct": 0.0487,
  "psi": {"age": 0.12, "total_purchases": 0.07, "avg_purchase_value": 0.18},
  "alerts": ["Caída relativa de AUC 5.1% ≥ 5%"],
  "generated_at": "2025-08-11T07:00:00Z"
}
```

---

## 🔔 Alertas (simuladas)
- El **exit code** distinto de cero permite disparar alertas desde el orquestador.
- Puedes añadir un *hook* HTTP/Slack/Email. Ejemplo (pseudocódigo Python):
```python
import json, os, requests
webhook = os.getenv("SLACK_WEBHOOK_URL")
rep = json.load(open("monitor_report.json"))
if rep["alerts"] and webhook:
    txt = "\n".join(["*ALERTAS de Monitoreo*", *rep["alerts"]])
    requests.post(webhook, json={"text": txt})
```

> En producción, centraliza logs en **Cloud Logging**, usa **Error Reporting** y notificaciones a **Slack/Email**.

---

## 🆚 Test A/B (simulación)
`ab_test_sim.py` ofrece:
- `evaluate_ab(df)` → calcula `accuracy`, `f1`, `roc_auc` para `v1` y `v2`.
- `pick_winner(metrics_dict, primary="roc_auc", secondary="f1")` → decide ganador.

**Flujo típico:**
1. Redirige un **% de tráfico** a `v2` (candidato).
2. Almacena predicciones (BigQuery) etiquetadas por variante.
3. Ejecuta `evaluate_ab` + `pick_winner` sobre la cohorte A/B.
4. Si `v2` ≥ `v1` en AUC y no peor en F1 → **promueve** `v2`.

---

## 🔁 Rollback & Split de Tráfico (Vertex AI)
**Política sugerida:**
- Rollback inmediato si:
  - `roc_auc` cae **≥ 10%** vs. baseline **o**
  - PSI **severo** en **≥ 2** features críticas.

**Ejemplo (Python, Vertex AI):**
```python
from google.cloud import aiplatform

project = "<PROJECT_ID>"
location = "us-central1"
endpoint_name = "projects/<PROJECT_ID>/locations/us-central1/endpoints/<ENDPOINT_ID>"

aiplatform.init(project=project, location=location)
endpoint = aiplatform.Endpoint(endpoint_name)

# Supongamos que el endpoint tiene despliegues: {"v1": 90, "v2": 10}
# Hacer rollback total a v1:
endpoint.update_traffic_split({"v1": 100})

# O hacer A/B 80/20:
endpoint.update_traffic_split({"v1": 80, "v2": 20})
```

**Ejemplo (gcloud):**
```bash
gcloud ai endpoints update-traffic-split \
  --project=<PROJECT_ID> \
  --location=us-central1 \
  <ENDPOINT_ID> \
  --traffic-split=\
"v1=90,v2=10"
```

> Mantén múltiples **Model Versions** registradas. Documenta claramente cuál es la *last known good* para revertir rápido.

---

## 🗄️ Persistencia y tableros (opcional recomendado)
- **BigQuery** como *feature store* liviano de predicciones:
  - Tabla `predictions_log(model_version STRING, inference_ts TIMESTAMP, y_proba FLOAT64, y_pred INT64, customer_id STRING, …)`
  - Tabla `ground_truth(customer_id STRING, y_true INT64, labeled_ts TIMESTAMP, …)`
- **Dashboards**: Looker Studio / Grafana sobre BigQuery para: AUC rolling, F1, PSI top-N, latencia, tasa de errores.

**Ejemplo de consulta de AUC diario (esbozo):**
```sql
SELECT
  DATE(inference_ts) AS day,
  APPROX_QUANTILES(y_proba, 100)[OFFSET(50)] AS median_score,
  COUNT(*) AS n
FROM dataset.predictions_log
GROUP BY day
ORDER BY day DESC;
```

---

## 🧰 Orquestación (opciones)
- **Cloud Run Job**: empaqueta `monitor_metrics.py` y dependencias en un contenedor.
- **Cloud Scheduler**: dispara el Job cada N minutos/horas.
- **Cloud Composer (Airflow)**: DAG con tareas de verificación, cálculo PSI y envío de alertas.

**Sugerencia de variables de entorno**
- `DATA_PATH` → ruta al batch actual (GCS/BigQuery extraído a CSV/Parquet).
- `THRESHOLDS_JSON` → archivo con umbrales custom.
- `SLACK_WEBHOOK_URL` → URL de webhook para notificaciones.

---

## 🧪 Validación de fin a fin
1. Genera `baseline_metrics.json`.
2. Ejecuta monitoreo con `--simulate-drift` y verifica:
   - `monitor_report.json` contenga PSI > 0.10 en alguna feature.
   - `alerts` no vacío.
   - Exit code = 1.
3. Ejecuta el notebook y confirma la simulación **A/B** y el bloque de **rollback**.

---

## ❓ FAQ
**¿De dónde salen los umbrales?**  
Parten de recomendaciones comunes (AUC ≥ 0.75 y PSI). Ajusta según tu dominio.

**¿Se puede integrar con Vertex Model Monitoring?**  
Sí. Este paquete es una simulación ligera y portable. Puedes migrar PSI y reglas a Vertex o a Grafana/Prometheus.

**¿Cómo guardo el reporte en BigQuery?**  
Parsea `monitor_report.json` y haz un `INSERT` a una tabla de auditoría.

---

## 🚧 Troubleshooting
- **"No existe baseline_metrics.json"** → ejecuta `--make-baseline` primero.
- **PSI NaN** → puede ser por baja varianza o columnas no numéricas; revisa bins.
- **AUC baja siempre** → revisa *data leakage*, balanceo de clases, o umbral de clasificación (0.5).

---

## ✅ Checklist de cumplimiento del Assessment
- **Métricas:** accuracy, precision, recall, f1, roc_auc.
- **Alertas:** por AUC mínimo, caída relativa y PSI (moderado/severo).
- **A/B testing:** función para evaluar v1 vs v2 y criterio de ganador.
- **Rollback:** política definida + ejemplos de **traffic split** (Vertex AI).
- **Documentación:** este README + notebook demostrativo.

---

## 📚 Referencias sugeridas
- Monitoreo de modelos: drift, data quality y concept drift (literatura MLOps general).
- PSI y KS en riesgo crediticio (metodología clásica, aplicable a churn con precaución).
- Documentación de Vertex AI Endpoints para **traffic split** y **model versions**.
