from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

# Cargar los datos
iris = load_iris()

# Crear y entrenar el modelo
modelo = LogisticRegression(max_iter=300)
modelo.fit(iris.data, iris.target)

# Crear la API
app = FastAPI(title="Clasificador de Flores")


class Flor(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


# Endpoint para verificar el servicio
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# Endpoint para realizar predicciones
@app.post("/predict")
def predict(flor: Flor):
    datos = [[
        flor.sepal_length,
        flor.sepal_width,
        flor.petal_length,
        flor.petal_width
    ]]

    prediccion = modelo.predict(datos)[0]

    return {
        "clase": str(iris.target_names[prediccion])
    }
