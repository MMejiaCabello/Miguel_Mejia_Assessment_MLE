import mlflow

THRESHOLD = 0.01  # Mínima mejora necesaria para reentrenar

mlflow.set_tracking_uri("http://127.0.0.1:5000")
experiment = mlflow.get_experiment_by_name("churn_prediction")

runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["metrics.f1_score DESC"])
best_f1 = runs.iloc[0]["metrics.f1_score"]

latest_f1 = runs.iloc[-1]["metrics.f1_score"]

if latest_f1 > best_f1 + THRESHOLD:
    print(f"Mejora detectada ({latest_f1} > {best_f1}). Proceder a reentrenar.")
else:
    print(f"No hay mejora significativa ({latest_f1} <= {best_f1 + THRESHOLD}).")
    