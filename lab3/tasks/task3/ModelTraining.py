import ray
from ray import tune
from sklearn.linear_model import SGDRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


@ray.remote
def train_model(config):
    X, y = make_regression(n_samples=10000, n_features=20, noise=0.1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = SGDRegressor(
        max_iter=config["max_iter"],
        tol=config["tol"],
        penalty=config["penalty"]
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    tune.report(mean_squared_error=mse)

def tune_model():
    analysis = tune.run(
        train_model,
        resources_per_trial={"cpu": 1},
        config={
            "max_iter": tune.grid_search([1000, 2000]),
            "tol": tune.grid_search([0.001, 0.0001]),
            "penalty": tune.grid_search(["l2", "l1"])
        }
    )
    return analysis.best_config

best_hyperparameters = ray.get(tune_model())


from ray import serve

class LinearModel:
    def __init__(self, hyperparameters):
        # Initialize the model with the best hyperparameters
        self.model = SGDRegressor(**hyperparameters)
        # Train the model with the full dataset (omitted for brevity)
        # ...

    def predict(self, inputs):
        # Perform prediction with the model
        return self.model.predict(inputs)

@serve.deployment
class ModelPredictor:
    def __init__(self):
        # Load the trained model (omitted for brevity)
        self.model = LinearModel(best_hyperparameters)

    async def __call__(self, request):
        json_input = await request.json()
        inputs = json_input["inputs"]
        prediction = self.model.predict(inputs)
        return {"prediction": prediction.tolist()}

# Deploy the model
serve.start()
ModelPredictor.deploy()

# Example request to the model server
import requests
response = requests.post("http://127.0.0.1:8000/ModelPredictor", json={"inputs": [[1, 2, 3, ...]]})
print(response.json())

