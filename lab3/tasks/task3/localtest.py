import ray
from ray import tune
from sklearn.linear_model import SGDRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

import os
os.environ["TUNE_DISABLE_STRICT_METRIC_CHECKING"] = "1"

@ray.remote
def process_data(data):
    processed_data = [x**2 for x in data]
    return processed_data

def train_model(config):
    try:
        X, y = make_regression(n_samples=100, n_features=20, noise=0.1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = SGDRegressor(
            max_iter=config["max_iter"],
            tol=config["tol"],
            penalty=config["penalty"]
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        print(f"Reporting MSE: {mse}")  # Debugging print
        tune.report(mean_squared_error=mse)
    except Exception as e:
        print(f"An error occurred in train_model: {e}")



def tune_model():
    analysis = tune.run(
        train_model,
        resources_per_trial={"cpu": 1},
        config={
            "max_iter": tune.grid_search([1000, 2000]),
            "tol": tune.grid_search([0.001, 0.0001]),
            "penalty": tune.grid_search(["l2", "l1"]),
        },
        num_samples=1,  # For debugging, you might start with a single sample
        verbose=1,
        metric="mean_squared_error",  # Specify the optimization metric
        mode="min",  # Specify that you want to minimize the metric
    )
    best_config = analysis.best_config
    return best_config


data = [1, 2, 3, 4, 5]

processed_data_future = process_data.remote(data)
processed_data = ray.get(processed_data_future)
print(f"Processed Data: {processed_data}")

# Tune the model
try:
    best_hyperparameters = tune_model()
    print(f"Best Hyperparameters: {best_hyperparameters}")
except Exception as e:
    print(f"An error occurred during hyperparameter tuning: {e}")
