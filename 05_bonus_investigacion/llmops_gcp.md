# LLMOps en GCP: Integración en una ML Factory

## ¿Qué es LLMOps?
Conjunto de prácticas para operar **Grandes Modelos del Lenguaje (LLMs)** en producción: desde el ajuste fino y adaptación (fine‑tuning/prompting) hasta despliegue, monitoreo, cumplimiento y control de costos. Extiende MLOps a flujos **generativos y multimodales**.

## Beneficios clave
- **Velocidad**: prototipado rápido vía prompt engineering y adapters (LoRA/PEFT).
- **Reutilización**: prompts y chains versionados como artefactos.
- **Calidad**: RAG + evaluación sistemática (golden sets, judge models).
- **Gobernanza**: auditoría de prompts, datos, políticas y costos.

## Arquitectura en GCP
- **Datos**: BigQuery (estructurado), GCS (no estructurado), Dataplex, Data Catalog.
- **Semántica**: Vertex AI **Embeddings** + **Matching Engine** para RAG.
- **Modelos**: Vertex AI **Model Garden**, **Tuning** y **Endpoints** o **Cloud Run**.
- **Orquestación**: Vertex **AI Pipelines**, **Cloud Scheduler**/**Pub/Sub**.
- **Observabilidad**: Cloud Logging/Monitoring, Vertex **Model Monitoring**, Looker Studio.
- **Seguridad**: IAM, VPC‑SC, CMEK, Secret Manager.

## Flujo simplificado
```bash
    Clientes/Apps → API (Cloud Run / Endpoints)
                ↓
         Orquestación (Vertex Pipelines)
                ↓
   RAG: Embeddings + Matching Engine ← Datos (BQ/GCS)
                ↓
       LLM Endpoint (Model Garden / Tuning)
                ↓
   Observabilidad (Logging / Monitoring / Looker)

```

## Integración en la ML Factory
1. **Repos & Versionado**: prompts, cadenas, evaluadores y adapters en Git + MLflow/DVC.
2. **Feature/Context Store**: Vertex **Feature Store** y Matching Engine.
3. **Pipelines**: KFP para índice vectorial, tuning, evaluación y despliegue.
4. **Inferencia**: online (Endpoint) y batch (Vertex Batch Predictions).
5. **Evaluación & QA**: métricas de factualidad, toxicidad, latencia, costo/token.

## Gobierno, riesgos y costos
- **Políticas**: catálogo de prompts aprobados, guardrails de uso.
- **Riesgos**: alucinaciones (mitigar con RAG), fuga de datos (DLP), sesgos.
- **Costos**: presupuestos, cuotas, caching y batching.

## Roadmap (6–8 semanas)
1. Baseline RAG y API en Cloud Run.
2. Evaluación automática y dashboards.
3. Tuning con adapters y control de versiones.
4. Hardening y SLOs/SLIs.

## KPIs sugeridos
- **Quality**: precisión factual@k, toxicidad < umbral.
- **Operación**: p95 latencia, disponibilidad.
- **Negocio**: CSAT/NPS, AHT reducido, costo por 1k tokens.

## Fuentes consultadas
- **Google Cloud**: [Vertex AI](https://cloud.google.com/vertex-ai) y [Model Garden](https://cloud.google.com/model-garden)
- **Google Cloud**: [Matching Engine](https://cloud.google.com/vertex-ai/docs/matching-engine/overview)
- **Papers**: "LLMOps: Operationalizing Large Language Models" – Stanford HAI 2023.
- **Blog**: [Google Cloud - Building RAG on GCP](https://developers.googleblog.com/es/vertex-ai-rag-engine-a-developers-tool)
- **Blog**: [Best Practices for Prompt Engineering](https://cloud.google.com/discover/what-is-prompt-engineering)
