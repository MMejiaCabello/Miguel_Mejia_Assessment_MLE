import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# Configuración de tracking
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("churn_prediction")

# Datos
df = pd.read_csv("../data/clientes.csv", parse_dates=["signup_date", "last_purchase_date"])
X = df.drop(columns=["churned", "customer_id"])
y = df["churned"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenamiento
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    f1 = f1_score(y_test, preds)

    # Log métricas y modelo
    mlflow.log_metric("f1_score", f1)
    mlflow.sklearn.log_model(model, "model")

    print(f"Modelo entrenado con F1-score: {f1}")
