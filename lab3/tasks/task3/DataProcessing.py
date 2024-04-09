import ray
from ray import tune
from ray import serve
from sklearn.linear_model import SGDRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error



@ray.remote
def process_data(data):
    processed_data = [x**2 for x in data]
    return processed_data

@ray.remote
def train_model(config):
    # Create synthetic data
    X, y = make_regression(n_samples=10000, n_features=20, noise=0.1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize model with hyperparameters
    model = SGDRegressor(
        max_iter=config["max_iter"],
        tol=config["tol"],
        penalty=config["penalty"]
    )

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    # Send the results back to Tune
    tune.report(mean_squared_error=mse)

# Use Ray Tune to find the best hyperparameters
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

from sklearn.linear_model import SGDRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

class LinearModel:
    def __init__(self, hyperparameters):
        # Initialize the SGDRegressor model with the best hyperparameters from tuning
        self.model = SGDRegressor(
            max_iter=hyperparameters['max_iter'],
            tol=hyperparameters['tol'],
            penalty=hyperparameters['penalty']
        )
        # Generate synthetic data for example purposes
        X, y = make_regression(n_samples=10000, n_features=20, noise=0.1)
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Train the model with the training data
        self.model.fit(X_train, y_train)

    def predict(self, inputs):
        # Perform prediction with the model
        predictions = self.model.predict(inputs)
        return predictions


from ray import serve
import numpy as np
import json

@serve.deployment
class ModelPredictor:
    def __init__(self, hyperparameters):
        # Instantiate the LinearModel with the tuned hyperparameters
        self.model = LinearModel(hyperparameters)

    async def __call__(self, request):
        # Extract the input data from the POST request
        json_input = await request.json()
        inputs = np.array(json_input["inputs"])
        # Use the LinearModel to predict
        prediction = self.model.predict(inputs)
        # Return the prediction as a JSON response
        return json.dumps({"prediction": prediction.tolist()})


# Deploy the model
serve.start()
ModelPredictor.deploy()

# Example request to the model server
import requests
response = requests.post("http://127.0.0.1:8000/ModelPredictor", json={"inputs": [[1, 2, 3, ...]]})
print(response.json())

